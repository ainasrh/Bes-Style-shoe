from rest_framework import serializers
from .views import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
import json
from .utils.s3_utils import upload_image_to_s3
from decouple import config
from django.conf import settings

User=get_user_model()
class RegSerializer(serializers.ModelSerializer):
    confirm_password=serializers.CharField(write_only=True,style={'input_type':'password'})
    
    class Meta:
        model=User
        fields=['username','email','password','confirm_password']

    def validate(self,data):
        password=data.get('password')
        confirm_password=data.get('confirm_password')    

        if password !=confirm_password:
            raise serializers.ValidationError({"confirm_password":"password Does Not Match"})
        
        return data
        
    # def create(self,data):
    #     user=User.object.create(username=data['username'])
    #     user.set_password(data['password'])
    #     user.save()

    #     return user

# Login Serializer

# class LoginSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls,user):
#         token=super().get_token(user)
#         token['username']=user.username
#         token['email']=user.email
#         return token

class LoginSerializer(serializers.Serializer):
    password=serializers.CharField(write_only=True)
    email=serializers.CharField(write_only=True)  
    def validate(self,data):
        email=data.get('email')
        password=data.get('password')
        print(email, password)

        user=authenticate(email=email,password=password)
        print("user",user)
        

        if not user:
            raise AuthenticationFailed('invalid user or password')
        
        
        # JWT generate

        refresh=RefreshToken.for_user(user)
        acces_token=str(refresh.access_token)
        

        return (
            {
                "message":'Login succesful',
                "user":{
                    'id':user.id,
                    'username':user.username,
                    'email':user.email,
                    'is_staff':user.is_staff,

                },
                'refresh':str(refresh),
                'acces_token':acces_token
            }
        )






    
#   PRODUCT SERIALIZER      


class ProductsSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    # print('serializer is working')

    class Meta:
        model = Products
        fields = ['id', 'name', 'price','image','image_url', 'details', 'size', 'stock','catagory']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be greater than zero')
        return value


    def get_image_url(self,obj):
        if obj.image:
            return obj.image.url
        return None
    
    # ensure size always array

    # def validate_size(self,value):
    #     if isinstance(value,list):
    #         try:
    #             value.json.loads(value)
    #         except json.JSONDecoderError:
    #             raise serializers.ValidationError('size must be a valid json array  (eg,[4,7,2,8])')
    #     return value

    def create(self,validated_data):
        image_file =validated_data.pop('image',None)
        print('image_file',image_file)


        if image_file:
            image_name=f'products/{image_file.name}'
            print('image_name',image_name)
            image_url=upload_image_to_s3(image_file,image_name)
            print('s3 url ',image_url)
            if not image_url:
                raise serializers.ValidationError('image upload failed')
            validated_data['image']=image_url
            print('final image data saved :',validated_data['image'])
        return super().create(validated_data) 
        
# CARTITEM SERIALIZER

class CartitemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(max_digits=20, decimal_places=2, source="product.price", read_only=True)
    product_image = serializers.ImageField(source="product.image", read_only=True)
    product_id = serializers.IntegerField(source="product.id")

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product_id",
            "product_name",
            "product_price",
            "product_image",
            # "product",
            "quantity",
            "total"
        ]

        # def to_representation(self,instance):
        #     data=super().to_representation(instance)

        #     # request=self.context.get('request')
        #     # if instance.product.image and request:
        #     #     data['product.image']=request(instance.product.image.url)
        #     # return data    

class CartSerializer(serializers.ModelSerializer): 
    username = serializers.CharField(source="user.username", read_only=True)
    cartItems = CartitemSerializer(many=True)

        
    class Meta:
        model = Cart
        fields = [
            "user",
            "username",
            "total_amount",
            "cartItems",
            

        ]



      

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")
    product_price = serializers.DecimalField(max_digits=10, decimal_places=2, source="product.price")
    product_image = serializers.SerializerMethodField()
    product_id=serializers.IntegerField(source="product.id")

    class Meta:
        model = OrderItem
        fields = [
            'product_id',
            'product_name',
            'product_price',
            'product_image',
            'quantity',
            'item_subtotal'
        ]

    def get_product_image(self,obj):
        request=self.context.get('request')
        if obj.product and obj.product.image:
            image_url = obj.product.image.url
            return request.build_absolute_uri(image_url) if request else image_url
        return None
    def get_product_id(self, obj):
        return obj.product.id if obj.product else None  

    def get_product_name(self, obj):
        return obj.product.name if obj.product else "Unknown Product"

    def get_product_price(self, obj):
        return obj.product.price if obj.product else 0.00 


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='order_items',many=True, read_only=True)
 
    

    class Meta:
        model = Order
        fields = [
            'user',
            'ordered_date',
            'status',
            'transaction_id',
            'items',
            
        ]      

    


# class ShippingAdressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=ShippingAddress
#         fields='__all__'        

class WishlistSerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(source="product.name",read_only=True)
    product_price=serializers.DecimalField(source='product.price',max_digits=10,decimal_places=2,read_only=True)
    product_image=serializers.SerializerMethodField()
    class Meta:
        model=WishList
        fields=[
            'id',
            'product_id',
            'product_name',
            'product_price',
            'product_image',
        ]  

    def get_product_image(self,obj):
        request=self.context.get('request')
        if obj.product.image:
            return request.build_absolute_uri(obj.product.image.url) if request else obj.product.image.url
        return None

class CheckoutSerializer(serializers.Serializer):
    # print('checkout serilaizer worked')
    # name=serializers.CharField(max_length=15)
    # address=serializers.CharField(max_length=200)
    # city=serializers.CharField(max_length=100)
    # state=serializers.CharField(max_length=100)
    # zipcode=serializers.IntegerField(min_value=1000,max_value=9999)
    shipping_address = serializers.DictField(child=serializers.CharField())
    # paymentMethod=serializers.CharField(max_length=100)

    def validate(self,data):
        cart=Cart.objects.filter(user=self.context['request'].user).first()
        cart_items=CartItem.objects.filter(cart=cart)
        print("requset data")

        if not cart_items :
            raise serializers.ValidationError('your cart is empty')
        
        if "shipping_address" not in data:
            raise serializers.ValidationError('Shipping Adress required')
        
        shipping_data=data['shipping_address']
        print('adrees recieved in serilaizer:',shipping_data)
        

        data['name']=shipping_data.get('name')
        data['address']=shipping_data.get('address')
        data['city']=shipping_data.get('city')
        data['state']=shipping_data.get('state')
        data['zipcode']=int(shipping_data["zipcode"])

        data["full_address"] = {
            "street_address": data["address"],
            "zipcode": data["zipcode"],
            "city": data["city"],
            "state": data["state"],
        }
         
         
        data['cart_items']=cart_items
        return data

        



class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=User
        fields=[
            'id',
            'username',
            'email',
            'is_staff',
            'last_login'
        ]

class DashBoardserializer(serializers.Serializer):
    product_count=serializers.IntegerField()
    orders_count=serializers.IntegerField()
    user_count=serializers.IntegerField()
    total_revenue=serializers.DecimalField(max_digits=13,decimal_places=2)

