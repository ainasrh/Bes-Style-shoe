from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image','details','stock','size')

admin.site.register(models.Order)
admin.site.register(models.OrderItem)
admin.site.register(models.ShippingAddress)
admin.site.register(models.WishList)

