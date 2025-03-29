
from django.urls import path,include
from .api_views import *
from .email_utils import verify_email

urlpatterns = [

    path('verify-email/<uidb64>/<token>/',verify_email,name='verify-email'),


    path('reg/',RegistertApi.as_view(),name='reg'),
    path('login/',LoginApi.as_view(),name='reg'),
    path('logout/',LogoutApi.as_view(),name='logout'),
    path('products/',ProductApi.as_view()),
    path('products/<int:pk>/',ProductApi.as_view()),
    path('products/<str:cat>/',ProductApi.as_view()),
    path('userdetails/',UserDetailsAPI.as_view()),
    path('category/<str:search>/',CatagoryApi.as_view()),
    path('cart/<int:pk>/',CartApi.as_view()),
    path('cart/',CartApi.as_view()),
    path('totalcart/',TotalCart.as_view()),
    path('orders/',CheckoutApi.as_view()),
    path('orders/<int:pk>/',CheckoutApi.as_view()),
    path('wishlist/',WishListApi.as_view()),
    path('wishlist/<int:pk>/',WishListApi.as_view()),
    # admin side //////

    path('allorders/',AllOrdersApi.as_view()),
    path('users/',Users.as_view()),
    path('users/<int:pk>/',Users.as_view()),
    path('dashboard/',DashBoardApi.as_view())
]