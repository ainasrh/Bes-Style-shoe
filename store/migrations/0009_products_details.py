# Generated by Django 5.1.4 on 2024-12-29 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_cart'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='details',
            field=models.TextField(default='product details'),
        ),
    ]
