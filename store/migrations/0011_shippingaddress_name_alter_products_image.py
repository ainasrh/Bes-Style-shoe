# Generated by Django 5.1.4 on 2024-12-30 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_products_size_products_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingaddress',
            name='name',
            field=models.CharField(default=None, max_length=200),
        ),
        migrations.AlterField(
            model_name='products',
            name='image',
            field=models.ImageField(blank=True, upload_to='products/'),
        ),
    ]
