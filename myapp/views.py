from django.shortcuts import render,redirect
from .models import Contact,User,Product,Wishlist,Cart,Transaction
from django.core.mail import send_mail
import random
from .paytm import generate_checksum, verify_checksum
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

def initiate_payment(request):
    user = User.objects.get(email=request.session['email'])
    try:
        amount = int(request.POST['amount'])
    except:
        return render(request, 'pay.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user, amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()
    carts = Cart.objects.filter(user=user, payment_status=False)
    for i in carts:
        i.payment_status = True
        i.save()
    carts = Cart.objects.filter(user=user, payment_status=False)
    request.session['cart_count'] = len(carts) 

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(
            paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)

# Create your views here.

def index(request):
	return render(request,'index.html')


def about(request):
	return render(request,'about.html')


def product(request):
	products=Product.objects.all()
	return render(request,'product.html',{'products':products})


def contact(request):
	if request.method=="POST":
		Contact.objects.create(
			name=request.POST['name'],
			email=request.POST['email'],
			mobile=request.POST['mobile'],
			message=request.POST['message'],
		)
		msg="Contact Saved Successfully!"
		contacts=Contact.objects.all().order_by("-id")[:3]
		return render(request,'contact.html',{'msg':msg, 'contacts':contacts})
	else:
		contacts=Contact.objects.all().order_by("-id")[:3]
		return render(request,'contact.html',{'contacts':contacts})


def signup(request):
	if request.method=="POST":
		try:
			User.objects.get(email=request.POST['email'])
			msg="Email Already Registered!"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
					usertype=request.POST['usertype'],
					fname=request.POST['fname'],
					lname=request.POST['lname'],
					email=request.POST['email'],
					mobile=request.POST['mobile'],
					address=request.POST['address'],
					password=request.POST['password'],
					profile_pic=request.FILES['profile_pic'],
				)
				msg="User Sign Up Successfully!"
				return render(request,'signup.html',{'msg':msg})
			else:
				msg="Password & Confirm Password Does Not Matched!"	
				return render(request,'signup.html',{'msg':msg})
	else:
		return render(request,'signup.html')


def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			if user.password==request.POST['password']:
				if user.usertype=="buyer":
					request.session['email']=user.email
					request.session['fname']=user.fname
					request.session['profile_pic'] = user.profile_pic.url
					wishlists=Wishlist.objects.filter(user=user)
					request.session['wishlist_count']=len(wishlists)
					carts=Cart.objects.filter(user=user,payment_status=False)
					request.session['cart_count']=len(carts)
					return render(request,'index.html')	
					
				else:
					request.session['email']=user.email
					request.session['fname']=user.fname
					request.session['profile_pic'] = user.profile_pic.url
					return render(request,'seller_index.html')
				
			else:
				msg="Incorrect Password!"
				return render(request,'login.html',{'msg':msg})
		except:
			msg="Email Not Registered!"
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')


def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		del request.session['profile_pic']
		return render(request,'login.html')
	except:
		return render(request,'login.html')


def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			otp=random.randint(1000,9999)
			subject = 'OTP for forgot password'
			message = 'Your OTP for forgot password is: '+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email, ]
			send_mail( subject, message, email_from, recipient_list )
			return render(request,'otp.html',{'otp':otp,'email':user.email})
		except:
			msg="Email Not Registered!"
			return render(request,'forgot_password.html',{'msg':msg})
	else:
		return render(request,'forgot_password.html')


def verify_otp(request):
	otp=request.POST['otp']
	uotp=request.POST['uotp']
	email=request.POST['email']
	if otp==uotp:
		return render(request,'new_password.html',{'email':email})

	else:
		msg="Invalid OTP!"
		return render(request,'otp.html',{'msg':msg,'otp':otp,'email':email})	


def new_password(request):
	email=request.POST['email']
	np=request.POST['new_password']
	cnp=request.POST['cnew_password']
	if np==cnp:
		user=User.objects.get(email=email)
		user.password=np
		user.save()
		msg="Password Updated Successfully!"
		return render(request,'login.html',{'msg':msg})
	else:
		msg="Password & Confirm Password Does Not Matched!"
		return render(request,'new_password.html',{'email':email,'msg':msg})


def change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		op=request.POST['old_password']
		np=request.POST['new_password']
		cnp=request.POST['cnew_password']
		if user.password==op:
			if np==cnp:
				user.password=np
				user.save()
				return redirect('logout')
			else:
				msg="New Password & Confirm New Password Does Not Matched!"
				return render(request,'change_password.html',{'msg':msg})
		else:
			msg="Old Password Does Not Matched!"
			return render(request,'change_password.html',{'msg':msg})
	else:
		return render(request,'change_password.html')


def profile(request):
    user = User.objects.get(email=request.session['email'])
    if request.method == "POST":
        user.fname = request.POST['fname']
        user.lname = request.POST['lname']
        user.mobile = request.POST['mobile']
        user.address = request.POST['address']
        try:
            user.profile_pic = request.FILES['profile_pic']
        except:
            pass
        user.save()
        request.session['profile_pic'] = user.profile_pic.url
        msg = "Profile Updated Successfully!"
        return render(request, 'profile.html', {'user': user, 'msg': msg})
    else:
        return render(request, 'profile.html', {'user': user})


def seller_profile(request):
    user = User.objects.get(email=request.session['email'])
    if request.method == "POST":
        user.fname = request.POST['fname']
        user.lname = request.POST['lname']
        user.mobile = request.POST['mobile']
        user.address = request.POST['address']
        try:
            user.profile_pic = request.FILES['profile_pic']
        except:
            pass
        user.save()
        request.session['profile_pic'] = user.profile_pic.url
        msg = "Profile Updated Successfully"
        return render(request, 'seller_profile.html', {'user': user, 'msg': msg})
    else:
        return render(request, 'seller_profile.html', {'user': user})


def seller_index(request):
	return render(request,'seller_index.html')

def seller_change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		op=request.POST['old_password']
		np=request.POST['new_password']
		cnp=request.POST['cnew_password']
		if user.password==op:
			if np==cnp:
				user.password=np
				user.save()
				return redirect('logout')
			else:
				msg='New Password & Confirm New Password Does Not Matched!'
				return render(request,'seller_change_password.html',{'msg':msg})
		else:
			msg="Old Password Does Not Matched!"
			return render(request,'seller_change_password.html',{'msg':msg})
	else:
		return render(request,'seller_change_password.html')

def seller_add_product(request):
	seller=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		Product.objects.create(
				seller=seller,
				product_category=request.POST['product_category'],
				product_name=request.POST['product_name'],
				product_price=request.POST['product_price'],
				product_desc=request.POST['product_desc'],
				product_pic=request.FILES['product_pic'],
			)
		msg="Product Added Successfully!"
		return render(request,'seller_add_product.html',{'msg':msg}) 
	else:
		return render(request,'seller_add_product.html')


def seller_view_product(request):
	seller=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=seller)
	return render(request,'seller_view_product.html',{'products':products})


def seller_product_detail(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller_product_detail.html',{'product':product})


def product_detail(request,pk):
	wishlist_flag=False
	cart_flag=False
	user=User()
	try:		
		user=User.objects.get(email=request.session['email'])
	except:
		return redirect('login')
	product=Product.objects.get(pk=pk)
	try:
		Wishlist.objects.get(user=user,product=product)
		wishlist_flag=True
	except:
		pass

	try:
		Cart.objects.get(user=user,product=product,payment_status=False)
		cart_flag=True
	except:
		pass

	return render(request,'product_detail.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})



def seller_edit_product(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":
		product.product_category=request.POST['product_category']
		product.product_name=request.POST['product_name']
		product.product_price=request.POST['product_price']
		product.product_desc=request.POST['product_desc']
		try:
			product.product_pic=request.FILES['product_pic']
		except:
			pass
		product.save()
		msg="Product Updated Successfully!"
		return render(request,'seller_edit_product.html',{'product':product,'msg':msg})
	else:	
		return render(request,'seller_edit_product.html',{'product':product})


def seller_delete_product(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	return redirect('seller_view_product')


def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	return render(request,'wishlist.html',{'wishlists':wishlists})

def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(product=product,user=user)
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)	
	return redirect('wishlist')


def remove_from_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return redirect('wishlist') 



def cart(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	net_price=0
	for i in carts:
		net_price=net_price+i.total_price
	return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(product=product,user=user,product_price=product.product_price,product_qty=1,total_price=product.product_price,payment_status=False)
	carts=Cart.objects.filter(user=user,payment_status=False)
	request.session['cart_count']=len(carts)	
	return redirect('cart')


def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('cart')


def change_qty(request):
	cid=int(request.POST['cid'])
	product_qty=int(request.POST['product_qty'])
	cart=Cart.objects.get(pk=cid)
	product_price=cart.product_price
	total_price=product_price * product_qty
	cart.product_qty=product_qty
	cart.total_price=total_price
	cart.save()
	return redirect('cart')


def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=True)
	return render(request,'myorder.html',{'carts':carts})
	


