# Generated by Django 5.1.4 on 2025-03-28 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_alter_products_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='image',
            field=models.ImageField(blank=True, max_length=500, null=True, upload_to='products/'),
        ),
    ]
