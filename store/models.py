from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Products(models.Model):
 
    name = models.CharField(max_length=100, null=True)
    price = models.FloatField()
    image = models.ImageField(blank=True, upload_to='products/')  # Saved in media/products/
    details=models.TextField(default='product details')
    size=models.JSONField()
    stock=models.IntegerField(default=100)
   

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    product = models.ForeignKey(Products, on_delete=models.CASCADE)  
    quantity = models.PositiveIntegerField(default=1)  
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} (x{self.quantity})"


class Order(models.Model):
    customer=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)   
    ordered_date=models.DateTimeField(auto_now_add=True)
    complete=models.BooleanField(default=False,blank=True,null=True)
    transaction_id=models.CharField(max_length=100,null=True)
    
    def __str__(self):
        return str(self.id)
    
class OrderItem(models.Model):
    product=models.ForeignKey(Products,on_delete=models.SET_NULL,blank=True,null=True)
    order=models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
    quantity=models.IntegerField(default=0,null=True,blank=True)   
    date_added=models.DateTimeField(auto_now_add=True) 

    @property
    def item_subtotal(self):
        return self.product.price*self.quantity

class ShippingAddress(models.Model):
    customer=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    name=models.CharField(max_length=200,default=None)
    order=models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
    address=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    zipcode=models.CharField(max_length=100)
    date_added=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
    

class WishList(models.Model):
    STATUS_CHOICE=(
        ('not available','not available'),
        ('in stock','in stock')
    )
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Products,on_delete=models.CASCADE)
    status=models.CharField(max_length=100,choices=STATUS_CHOICE,default='in stock')
    

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"