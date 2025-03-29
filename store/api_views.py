import razorpay
from .serializer import *
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate,login,logout
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView 
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from django.db.models import F
from django.contrib.auth import get_user_model
from .email_utils import send_verification_email
from razorpay import Client
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.parsers import MultiPartParser


User=get_user_model()





class RegistertApi(APIView):
    permission_classes=[AllowAny]
    # print('register working')

    def post(self,request):
        serializer=RegSerializer(data=request.data)
        if serializer.is_valid():

            user=User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )

            user.is_active=False
            user.save()
            send_verification_email(user,request)
            return Response({'message':"Registration Successfully completed Check your Email for verification Link"},status=status.HTTP_201_CREATED)
        return Response({"message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    

class LoginApi(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serialized=LoginSerializer(data=request.data)
        serialized.is_valid(raise_exception=True)
        
        return Response(serialized.validated_data,status=status.HTTP_200_OK)

class LogoutApi(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        try:
            
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "You have successfully logged out"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
        


class ProductApi(APIView):
    parser_classes=[MultiPartParser]


        #GET API


    def get(self,request,pk=None):
        permission_classes=[AllowAny]
        if pk:
            
            try:
                product = Products.objects.get(id=pk)
                serialized = ProductsSerializer(product,context={'request':request})
                return Response(serialized.data, status=status.HTTP_200_OK)
            except Products.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
           
            products = Products.objects.all()
            serialized = ProductsSerializer(products, many=True,context={'request':request})
            return Response(serialized.data, status=status.HTTP_200_OK)
        


    def post(self, request):
        permission_classes =[IsAdminUser]
        # pass request data and file data (image)
        
        if not request.user.is_staff:
            return Response({'error':' you do not have permission to create product'},status=status.HTTP_403_FORBIDDEN)
        
        # handling  size conversion 
        if 'size' in request.data and isinstance(request.data['size'],str):
            try:
                request.data['size']=json.loads(request.data['size'])
            except json.JSONDecodeError:
                request.data['size']=[]
        print('request data :  ',request.data)
        serializer=ProductsSerializer(data=request.data)
        
        if serializer.is_valid():
            # for call create function inside of serializer
            serializer.save()
            return Response({'message': "Product Successfully Created"}, status=status.HTTP_201_CREATED)
        print('not valid ',serializer.errors)
        return Response({'error':'not valid data'}, status=status.HTTP_400_BAD_REQUEST)

    
    
    
    #PUT API

    
    def put(self,request,pk=None):
        # authentication_classes =[JWTAuthentication]
        # ermission_classes =[IsAuthenticated]
        # if not request.user.is_staff:
        #     return Response({'error':' you do not have permission to update product'},status=status.HTTP_403_FORBIDDEN)
        try:
            product_obj=Products.objects.get(id=pk)
        except Products.DoesNotExist:
            return Response({'error':'product not found'},status=status.HTTP_404_NOT_FOUND)
        
        data=ProductsSerializer(product_obj,data=request.data)
        
        if data.is_valid():
            product_obj.name=data.validated_data['name']
            product_obj.price=data.validated_data['price']
            product_obj.image=data.validated_data['image']
            product_obj.details=data.validated_data['details']
            product_obj.size=data.validated_data['size']
            product_obj.stock=data.validated_data['stock']

            product_obj.save()
            # data.save()
            return Response({'messgae':'Product Succesfully Updated'},status=status.HTTP_200_OK) 
        return Response({'message':'data is not valid'})
    
    #PARTIAL API 

    # def patch(self,request,pk=None):
    #     try:
    #         product_obj=Products.objects.get(id=pk)
    #     except Products.DoesNotExist:
    #         return Response({'error':'product does not found '},status=status.HTTP_404_NOT_FOUND)
    #     data=ProductsSerializer(product_obj,data=request.data,partial=True)
    #     if data.is_valid():
    #         data.save()
    


    #DELETE API

    def delete(self,request,pk=None):
        # authentication_classes =[JWTAuthentication]
        # permission_classes =[IsAuthenticated]
        # if not request.user.is_staff:
        #     return Response({'error':' you do not have permission to delete product'},status=status.HTTP_403_FORBIDDEN)
        try:
            data=Products.objects.get(id=pk).delete()
        except Products.DoesNotExist:
            return Response({'error':'product not found'},status=status.HTTP_404_NOT_FOUND) 
           
        return Response({'message':'product succefully deleted'},status=status.HTTP_204_NO_CONTENT)


    #USER DETAILS
class UserDetailsAPI(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        user=request.user
        return Response(
            {
                "id":user.id,
                "username":user.username,
                "email":user.email,
                "is_staff":user.is_staff

            }
        )
        
class BlockUnblockUser(APIView):
    pass     

#----------CATAGORY------

class CatagoryApi(APIView):
    permission_classes=[AllowAny]
    
    def get(self,request,search=None):
        if search is None:
            return Response({'error':'product not found'},status=status.HTTP_404_NOT_FOUND)
        
        data=Products.objects.filter(Q(catagory__icontains=search))
        serialized=ProductsSerializer(data,many=True,context={"request":request})
        return Response(serialized.data,status=status.HTTP_200_OK)
    

#-----------CART---------

class CartApi(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,pk=None):
        
        if not pk:
            try:
                cart=Cart.objects.filter(user=request.user).first()
            except Cart.DoesNotExist:
                return Response({'error':'cart is empty'},status=status.HTTP_400_BAD_REQUEST)    
        
            serialized=CartSerializer(cart,context={'request':request})
            return Response(serialized.data,status=status.HTTP_200_OK)
    

   #-----create product---- 

    # def post(self, request):
    #     cart, created = Cart.objects.get_or_create(user=request.user)
    #     serializer = CartitemSerializer(data=request.data)

    #     if serializer.is_valid():
    #         product_id = serializer.validated_data.get("product")
    #         print("product",serializer.validated_data)
    #         quantity = serializer.validated_data.get("quantity")

    #         try:
    #             product = Products.objects.get(id=product_id)

    #         except Products.DoesNotExist:
    #             return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    #         cart_item, created = CartItem.objects.get_or_create(
    #             cart=cart,
    #             product=product,
    #             defaults={"quantity": quantity}
    #         )

    #         if not created:
    #             cart_item.quantity += quantity
            
    #         cart_serializer = CartSerializer(cart)
    #         return Response(cart_serializer.data, status=status.HTTP_200_OK)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        print(request.data,'cart post worked')
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartitemSerializer(data=request.data)

        if serializer.is_valid():
            product_id = serializer.data.get("product_id")
            quantity = serializer.data.get("quantity")
            # print("product",serializer.data)
            # print("product",product_id)

            try:
                product = Products.objects.get(id=product_id)
            except Products.DoesNotExist:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    
            if quantity > product.stock:
                return Response({"error": "Requested quantity exceeds available stock"}, status=status.HTTP_400_BAD_REQUEST)

        
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={"quantity": quantity}
            )

            if not created:
                if cart_item.quantity + quantity > product.stock:
                    return Response({"error":"requested quantity exceeds available in stock"},status=status.HTTP_400_BAD_REQUEST)
                cart_item.quantity += quantity
                cart_item.save()

            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    
    def delete(self, request, pk):
        
        try:

            cartitem = CartItem.objects.get(cart__user=request.user,product__id=pk)
             
            
            cartitem.delete()
            
            return Response({'message': 'Item deleted successfully'}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item does not exist'}, status=status.HTTP_404_NOT_FOUND)

        
    def patch(self,request,pk):
        # increase and decrease qauntity 
        # print(request.data)
        action=request.data.get('action',"").lower()

        if action not in ['increase','decrease']:
            return Response({'error':'invalid Action . Use "increase or decrease"'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart_item=CartItem.objects.get(cart__user=request.user,product__id=pk)
        except CartItem.DoesNotExist:
            return Response({'error':'Cart Item not found '},status=status.HTTP_404_NOT_FOUND)
        if action=="increase":
            if cart_item.quantity + 1 > cart_item.product.stock:
                return Response({'error':'requested quantity  exceeds available stock '},status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity += 1
        elif action=='decrease':
            if cart_item.quantity > 1:
                cart_item.quantity-=1
            else:
                cart_item.delete()
                return Response({'message':"item removed succesfully"},status=status.HTTP_200_OK)
        cart_item.save()
        return Response({'message':f'item quantity {action}d successfully'},status=status.HTTP_200_OK)            


class TotalCart(APIView):
    permission_classes=[IsAdminUser]
    def get(self,request):
        cart=Cart.objects.all()
        serializer=CartSerializer(cart,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
            

#-----ORDER-------- CHECKOUT---------

class CheckoutApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(request.user)
        user = request.user
        order_items = OrderItem.objects.filter(order__user=user).select_related("product", "order")

        if not order_items.exists():
            return Response({"message": "No order items found."}, status=status.HTTP_404_NOT_FOUND)

        
        serializer = OrderItemSerializer(order_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    # def post(self, request, *args, **kwargs):

    #     print('recieved data to order api',request.data)
    #     serializer = CheckoutSerializer(data=request.data, context={"request": request})
    #     if serializer.is_valid():
    #         cart_items = serializer.validated_data["cart_items"]
    #         address=serializer.validated_data['full_address']
    #         # payment_data=serializer.validated_data['paymentMethod']

    #         order_data = {  
    #             "user": request.user,
    #             "status": Order.StatusChoices.PENDING,
    #             "address":address
    #         }

    #         try:
    #             with transaction.atomic():
    #                 order = Order.objects.create(**order_data)
    #                 total_amount = 0
    #                 order_items = []
    #                 product_update = []
    #                 for cart_item in cart_items:
    #                     product = cart_item.product
    #                     quantity = cart_item.quantity

    #                     if product.stock < quantity :
    #                         raise serializers.ValidationError(
    #                             f"Insufficient stock for {product.name}",
    #                             status=status.HTTP_400_BAD_REQUEST
    #                         )
                        
    #                     order_items.append(
    #                         OrderItem(order=order, product=product, quantity=quantity )
    #                     )
                        
    #                     product.stock=F('stock')-quantity
    #                     product_update.append(product)
    #                     total_amount += product.price * quantity

    #                     OrderItem.objects.bulk_create(order_items)
    #                     Products.objects.bulk_update(product_update,['stock'])

    #                     cart_items.delete()

    #                     # Razorpay integration 
    #                     client=Client(
    #                         auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_SECRET_KEY)
    #                     )
    #                     razorpay_order=client.order.create(
    #                         {
    #                             'amount':int(total_amount * 100), # convert total amount into rupee
    #                             'currency':"INR",
    #                             # 'reciept':str(order.order_id),
    #                             'payment_capture':1,
    #                         }
                            
    #                     ) 
    #                     order.transaction_id=razorpay_order['id']
    #                     order.save()

                        
                    
    #                 # create new shpping adress

    #                 # shipping_address =ShippingAddress.objects.create(
    #                 #     customer=request.user,
    #                 #     order=order,
    #                 #     name=shipping_data['name'],
    #                 #     adress=shipping_data['address'],
    #                 #     state=shipping_data['state'],
    #                 #     zipcode=shipping_data['zipcode']
    #                 # )
                    

    #                 return Response(
    #                     {
    #                         "razorpay_order":razorpay_order,
    #                         "order_details": OrderSerializer(order).data,
                            
    #                     },
    #                     status=status.HTTP_201_CREATED,
    #                 )
    #         except Exception as e:
    #             return Response(
    #                 {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #             )
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        print('received data to order api', request.data)
        serializer = CheckoutSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            cart_items = serializer.validated_data["cart_items"]
            address = serializer.validated_data['full_address']

            order_data = {
                "user": request.user,
                "status": Order.StatusChoices.PENDING,
                "address": address,
            }

            try:
                with transaction.atomic():
                    # Create the order
                    order = Order.objects.create(**order_data)
                    total_amount = 0
                    order_items = []
                    product_update = []

                    for cart_item in cart_items:
                        product = cart_item.product
                        quantity = cart_item.quantity

                        # Check stock availability
                        if product.stock < quantity:
                            raise serializers.ValidationError(
                                f"Insufficient stock for {product.name}",
                                status=status.HTTP_400_BAD_REQUEST
                            )

                        # Create OrderItem instance (do not manually assign 'id')
                        order_items.append(
                            OrderItem(order=order, product=product, quantity=quantity)
                        )

                        # Update product stock
                        product.stock = F('stock') - quantity
                        product_update.append(product)
                        total_amount += product.price * quantity

                    # Bulk create OrderItems
                    OrderItem.objects.bulk_create(order_items)

                    # Bulk update product stock
                    Products.objects.bulk_update(product_update, ['stock'])

                    # Delete cart items
                    cart_items.delete()

                    # Razorpay integration


                    client = Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
                    razorpay_order = client.order.create({
                        'amount': int(total_amount * 100),  # Convert total amount into paise
                        'currency': "INR",
                        'payment_capture': 1,
                    })

                    # Save Razorpay order ID to the order
                    order.transaction_id = razorpay_order['id']
                    order.save()


                    # Send Email to the user after payment
                    subject="Order Confirmation"
                    html_message=render_to_string('order_confirmation_email.html',{
                        "user":request.user,
                        'order':order,
                        "total_amount":total_amount
                    })

                    plain_message=strip_tags(html_message)

                    from_email=settings.DEFAULT_FROM_EMAIL
                    to_email=request.user.email

                    send_mail(
                        subject,
                        plain_message,
                        from_email,
                        [to_email],
                        html_message=html_message ,
                        fail_silently=False
                    )

                    return Response(
                        {
                            "razorpay_order": razorpay_order,
                            "order_details": OrderSerializer(order).data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk=None):
        try:
            print(request.user)
            print(pk)
            order_item = OrderItem.objects.get(product__id=pk,order__user=request.user)
            print('order')
            order_item.delete()
            return Response({'message': 'Order item deleted successfully'}, status=status.HTTP_200_OK)
        
        except OrderItem.DoesNotExist:
            return Response({'error': 'Order item not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND) 
        

class WishListApi(APIView):
    def get(self,request):
        wishlist_item=WishList.objects.filter(user=request.user)
        serialized=WishlistSerializer(wishlist_item,many=True,context={'request':request})
        return Response(serialized.data,status=status.HTTP_200_OK)
        
    def post(self,request,pk):
        print(request,pk,'wishlist post worked')
        try:
            if not pk:
                return Response({'error':'product ID is required '},status=status.HTTP_400_BAD_REQUEST)
            
            product=Products.objects.get(id=pk)
            wishlist_item,created=WishList.objects.get_or_create(user=request.user,product=product)
            if created:
                return Response({'message':'product  added to wishlist '},status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'product already added in your list '},status=status.HTTP_200_OK)
        except Products.DoesNotExist:
            return Response({'error':'Product not found '},status=status.HTTP_404_NOT_FOUND)
        
    def delete(self,request,pk):
        try:
            wishlist_item=WishList.objects.get(user=request.user,product=pk)
            wishlist_item.delete()
            return Response({'message':'product removed form wishlist'},status=status.HTTP_200_OK)
        except WishList.DoesNotExist:
            return Response({'error':'product not found in wishlist'},status=status.HTTP_404_NOT_FOUND)
                
 
                



# Admin side ////////////

class AllOrdersApi(APIView):
    permission_classes=[IsAdminUser]
    def get(self,request):
        AllOrders=OrderItem.objects.all()
        serializer_order=OrderItemSerializer(AllOrders,many=True,context={'request':request})
        if serializer_order.data:
            return Response(serializer_order.data,status=status.HTTP_200_OK)
        return Response({'error':'errror in fetching all order'},status=status.HTTP_400_BAD_REQUEST)

class Users(APIView):
    permission_classes=[IsAdminUser]
    def get(self,request):
        AllUsers=User.objects.all()
        serialized_users=UserSerializer(AllUsers,many=True)
        if serialized_users.data:
            return Response(serialized_users.data,status=status.HTTP_200_OK)
        else:
            return Response({'error':'error from fecthing all Users'},status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        user=User.objects.get(id=pk)
        if user:
            user.delete()
            return Response({'response':'User deleted Succesfully'},status=status.HTTP_200_OK)
        return Response({'error':"error from deleting user"},status=status.HTTP_404_NOT_FOUND)
    

class DashBoardApi(APIView):
    def get(self,request):
        product_count=Products.objects.all().count()
        orders_count=Order.objects.all().count()
        user_count=User.objects.filter(Q(is_superuser=False) & Q(is_staff=False)).count()
        orders_items=OrderItem.objects.all()
        total_revenue=sum(item.item_subtotal for item in orders_items)

        data={
            'product_count':product_count,
            'orders_count':orders_count,
            'user_count':user_count,
            'total_revenue':total_revenue
        }
        serialized=DashBoardserializer(data)
        return Response(serialized.data,status=status.HTTP_200_OK)
    





       



