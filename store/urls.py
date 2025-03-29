from django.urls import path,include
from . import views as v
from .api_views import *
from .email_utils import verify_email


urlpatterns = [

    # VERIFY EMAIL 


    path('',v.store,name='store'),
    path('signup/',v.register,name='signup'),
    path('login/',v.login_view,name='login'),
    path('logout/',v.logout_view,name='logout'),
    path('cart/',v.cart_view,name='cart'),
    path('checkout/',v.checkout,name='checkout'),
    path('wishlist/',v.wishlist_View,name='wishlist'),
    path('products/',v.all_products,name='products'),
    path('get_category',v.get_category,name='get_category'),
    path('add_wishlist/<int:product_id>/',v.add_wishlist,name='add_wishlist'),
    path('delete_wishlist/<int:product_id>/',v.remove_wishlist,name='remove_wishlist'),
    path('add_to_cart/<int:product_id>/',v.cart_add, name='add_to_cart'),
    path('remove_cart/<int:product_id>/',v.remove_cart,name='remove_cart'),
    path('increment_quantity/<int:product_id>/',v.increase_quantity,name='increment_quantity'),  #quantity increment
    path('decrease_quantity/<int:product_id>/',v.decrease_quantity,name='decrement_quantity'),   
    path('product/<int:product_id>/', v.product_detail, name='product_detail'),
    path('order-success/',v.order_success, name='order_success'),
    path('admin_products/',v.admin_products,name='admin_products'),
    path('product_update/<int:product_id>',v.update,name='update'),
    path('product_delete/<int:product_id>',v.delete,name='delete'),
    path('user/',v.users_view,name='user'),
    path('dashboard/',v.dashboard,name='dashboard'),
    path('user_delete/<int:user_id>/',v.user_delete,name='user_delete'),
    path('user_update/<int:user_id>/',v.user_update,name='update_user'),
    path('orders/',v.orders_view,name='orders'),
    path('create/',v.create,name='create'),

    # API URLS

    

]