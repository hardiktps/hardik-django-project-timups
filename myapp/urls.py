from django.urls import path
from . import views

urlpatterns = [
    
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('product/',views.product,name='product'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('new_password/',views.new_password,name='new_password'),
    path('change_password/',views.change_password,name='change_password'),
    path('profile/',views.profile,name='profile'),
    path('selelr_profile/',views.seller_profile,name='seller_profile'),
    path('seller_index/',views.seller_index,name='seller_index'),
    path('seller_change_password/',views.seller_change_password,name='seller_change_password'),
    path('seller_add_product/',views.seller_add_product,name='seller_add_product'),
    path('seller_view_product/',views.seller_view_product,name='seller_view_product'),
    path('seller_product_detail/<int:pk>/',views.seller_product_detail,name='seller_product_detail'),
    path('seller_edit_product/<int:pk>/',views.seller_edit_product,name='seller_edit_product'),
    path('seller_delete_product/<int:pk>/',views.seller_delete_product,name='seller_delete_product'),
    path('product_detail/<int:pk>/',views.product_detail,name='product_detail'),
    path('add_to_wishlist/<int:pk>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('wishlist',views.wishlist,name='wishlist'),
    path('remove_from_wishlist/<int:pk>/',views.remove_from_wishlist, name='remove_from_wishlist'),
    path('add_to_cart/<int:pk>/',views.add_to_cart,name='add_to_cart'),
    path('cart',views.cart,name='cart'),
    path('remove_from_cart/<int:pk>/',views.remove_from_cart, name='remove_from_cart'),
    path('change_qty/',views.change_qty,name='change_qty'),
    path('pay/',views.initiate_payment, name='pay'),
    path('callback/',views.callback, name='callback'),
    path('myorder/',views.myorder,name='myorder'),

]

