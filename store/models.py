from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib.auth.models import AbstractUser
from .manager import UserManager

# Create your models here.

# User model


class User(AbstractUser):
    username=models.CharField(max_length=100)
    email=models.CharField(unique=True,max_length=100)
    phone=models.CharField(max_length=12)
    is_email_verified=models.BooleanField(default=False)
    email_verification_token=models.CharField(max_length=200,null=True,blank=True)
    forgot_password_token=models.CharField(max_length=200,null=True,blank=True)
 

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    objects=UserManager()

    # def name(self):
    #     return self.first_name+" "+ self.last_name

    def __str__(self):
        return self.email


class Products(models.Model):
    # size_choices=(
    #     ('5','5'),
    #     ('6','6'),
    #     ('7','7'),
    #     ('8','8'),
    #     ('9','9'),
    #     ('10','10')

    # )
 
    name = models.CharField(max_length=100, null=True)
    price = models.FloatField()
    image = models.ImageField(null=True,blank=True)  # Saved in media/products/
    details=models.TextField(default='product details')
    size=models.JSONField(default=list)
    stock=models.IntegerField(default=100)
    catagory=models.CharField(max_length=200)

    
    @property
    def in_stock(self):
        return self.stock > 0


    # def get_image(self):
    #     if self.image: 
    #         return self.image.url
    #     return "no image available"

   

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_amount(self):
        return sum(item.total for item in self.cartItems.all())

    def __str__(self):
        return f"{self.user.username}"

    
class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="cartItems")
    product = models.ForeignKey(Products, on_delete=models.CASCADE,null=False,blank=False) 
    quantity = models.PositiveIntegerField(default=1)
    
    

    def __str__(self):
        return self.product.name
    
    @property
    def total(self):
        return self.product.price * self.quantity


 
class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending",
        COMPLETED = "completed",
        CANCELLED = "cancelled"

    order_id=models.UUIDField(primary_key=True, default=uuid.uuid4,unique=True)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)   
    ordered_date=models.DateTimeField(auto_now_add=True)
    status= models.CharField(max_length=15, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    products=models.ManyToManyField(Products,through='OrderItem',related_name='orders')
    address=models.JSONField(default=dict)
    transaction_id=models.CharField(max_length=100,null=True,blank=True)

    
    def __str__(self):
        return str(self.user) 
    
class OrderItem(models.Model):
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, blank=True, null=True)
    order=models.ForeignKey(Order,on_delete=models.SET_NULL,related_name="order_items",blank=True,null=True)
    quantity=models.IntegerField(default=0,null=True,blank=True)   
    is_cancelled=models.BooleanField(default=False)
    
    
    @property
    def  item_subtotal(self):
        return self.product.price*self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.order.order_id}"

# class ShippingAddress(models.Model):
#     customer=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
#     name=models.CharField(max_length=200,default=None)
#     order=models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
#     address=models.CharField(max_length=100)
#     state=models.CharField(max_length=100)
#     city=models.CharField(max_length=100)
#     zipcode=models.CharField(max_length=100)
#     date_added=models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.address
    

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