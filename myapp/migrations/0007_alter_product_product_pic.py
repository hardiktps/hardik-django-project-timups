# Generated by Django 4.1.7 on 2023-02-20 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_pic',
            field=models.ImageField(default='', upload_to='product_pic/'),
        ),
    ]
