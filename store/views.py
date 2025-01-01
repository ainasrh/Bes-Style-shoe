from django.contrib import messages
from .forms import *
from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.db.models import Q
from .forms import Register_form,login_form
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from rest_framework import status
import uuid

# Create your views here.

# MAIN

# def main_view(request):
#     wishlist_count=WishList.objects.filte(user=request.user).count()
#     cart_count=Cart.objects.filter(user=request.user).count()
#     return render(request,'store/main.html',wishlist_count,cart_count)
    # REGISTER

def register(request):
    if request.method=='POST':
        form=Register_form(request.POST)
        if form.is_valid():
            username=form.cleaned_data.get('name')
            email=form.cleaned_data.get('email')
            password=form.cleaned_data.get('password')
            password2=form.cleaned_data.get('confirm_password')

            # Check  username is already taken
            if User.objects.filter(username=username).exists():
                error = 'This username is already taken.'
                return render(request, 'register.html', {'form': form, 'user_error': error})
            
            # Check  email 
            if User.objects.filter(email=email).exists():
                error = 'This email is already registered.'
                return render(request, 'register.html', {'form': form, 'email_error': error})
            

            if password==password2:

                user=User(username=username,email=email)
                

                user.set_password(password)

                user.save()

                user=authenticate(request,username=username,password=password)
                if user:
                    login(request,user)
                    return redirect('store')
            else:
                error='password  and confirm passwrod must be same'
                return render(request,'register.html',{'form':form,'pass_error':error})
    else:

        form=Register_form()

    return render(request,'register.html',{"form":form})

    # LOGIN VIEW
def login_view(request): 
    error=''
    if request.method=='POST':
        form=login_form(request.POST)
        if form.is_valid():
            name=form.cleaned_data.get('name')
            password=form.cleaned_data.get('password')
            
            user=authenticate(request,username=name,password=password)
            if user and user.is_superuser:
                login(request,user)
                return redirect('dashboard')
            elif user:
                login(request,user)
                return redirect('store')
        
            else:
                error='check username or password'
    else:

        form=login_form()
    
    return render(request,'login.html',{'form':form,'login_error':error})

    # LOGOUT
def logout_view(request):
    logout(request)
    return redirect('store')


# DISPLAY CATAGORY WISE

    # adidas
def get_category(request):
    category=request.GET.get('name',None)

    if category:
        item=Products.objects.filter(name__icontains=category)
        print("its working", category)
    else:
        print("its not working", request.GET)
        return redirect('products')    

    return render(request,'store/products.html',{'products':item})

    # STORE

def store(request):
    if 'search_data' in request.GET:
        search=request.GET['search_data']
        data=Products.objects.filter(Q(name__icontains=search) | Q(price__icontains=search))
        if data:
            return render(request,'store/products.html',{'products':data})
        else:
            not_available="search not found"
            return render(request,'store/products.html',{'products':data,'not_available':not_available})
    return render(request,'store/store.html')


    # ALL PRODUCTS
def all_products(request):
    search_error = ''  
    search = request.GET.get('search_data', None) 

    
    data = Products.objects.all()

    if search:  
        data = Products.objects.filter( Q(name__icontains=search) | Q(price__icontains=search))
    
        if not data.exists():
            search_error = 'Products not found'

    return render(request, 'store/products.html', {
        'products': data,
        'search_error': search_error,
    })


    # CART_ADD
@login_required(login_url='/login/')
def cart_add(request,product_id):
    item=get_object_or_404(Products,pk=product_id)
    cart_item,created=Cart.objects.get_or_create(user=request.user,product=item)

    if  created:
        WishList.objects.filter(user=request.user,product=item).delete()
        messages.success(request,f'{item.name} has been added to your Cart')
        # return HttpResponse(status=status.HTTP_200_OK)
        return redirect('products')
    
    else:
        messages.info(request,f'{item.name} already exists in your cart')    
        return redirect('products')
        # return HttpResponse(status=status.HTTP_200_OK)

def remove_cart(request,product_id):
    pk=product_id
    Cart.objects.filter(id=pk).delete() #remove

    messages.success(request,f" has been successfully deleted")
    return redirect('cart')

    # CART VIEW
@login_required(login_url='/login/')
def cart_view(request):

    product=Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in product)


    return render(request,'store/cart.html',{'cart_items':product,'cart_count':product.count(),'cart_total':total_price})

    # INCREMENT QUANTITY

def increase_quantity(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.quantity += 1
    cart_item.save()
    # messages.success(request, f"The quantity of {cart_item.product.name} has been increased.")
    return redirect('cart')

# decrease_quantity

def decrease_quantity(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        # messages.success(request, f"The quantity of {cart_item.product.name} has been decreased.")
    else:
        cart_item.delete() 
        messages.info(request, f"{cart_item.product.name} has been removed from your cart.")
    return redirect('cart')





 
    # ADD WISHLIST
@login_required(login_url='login')
def add_wishlist(request,product_id):
    item=get_object_or_404(Products,pk=product_id)
    wishlist_item=WishList.objects.get_or_create(user=request.user,product=item)

    if  wishlist_item:
        messages.success(request,f'{item.name} has been added to your wishlist')
    else:
        messages.info(request,f'{item.name} already exists')    

    return redirect('products')

    # REMOVE WISHLIST
@login_required(login_url='login')
def remove_wishlist(request,product_id):
    pk=product_id
    WishList.objects.filter(id=pk).delete() #remove

    messages.success(request,f" has been successfully deleted")
    return redirect('wishlist')

    # COUNT WISHLIST

def wishlist_View(request):
    
    data=WishList.objects.filter(user=request.user)

    return render(request,'store/wishlist.html',{'wish_products':data,'wishlist_count':data.count()})

def product_detail(request,product_id):
    product=get_object_or_404(Products,pk=product_id)

    return render(request,'store/product_Detail.html',{'product':product})

   # CHECKOUT

@login_required(login_url='login')
def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)


    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        
        name = request.POST.get('name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')


        order = Order.objects.create(
            customer=request.user,
            transaction_id=str(uuid.uuid4()),  
            complete=False
        )

        
        for item in cart_items:
            OrderItem.objects.create(
                product=item.product,
                order=order,
                quantity=item.quantity
            )

     
        ShippingAddress.objects.create(
            customer=request.user,
            order=order,
            name=name,
            address=address,
            city=city,
            state=state,
            zipcode=zipcode
        )

    
        cart_items.delete()

        
        messages.success(request, 'Order placed successfully!')
        return redirect('order_success')

    context = {
        'products': cart_items,
        'checkout_count': cart_items.count(),
        'checkout_sum': total_price
    }
    return render(request, 'store/checkout.html', context)

@login_required(login_url='login')
def order_success(request):
    return render(request, 'store/order_success.html')


def admin_products(request):
    all_products=Products.objects.all()
    return render(request,'admin_dashboard/products.html',{'all_products':all_products})


def update(request,product_id):
    
    upd = get_object_or_404(Products, id=product_id)
    print('1')
    
    if request.method == 'POST':
        
        form = ProductForm(request.POST, instance=upd)
        print('2')
        if form.is_valid():
            
            form.save()
            
            return redirect('admin_products')
    else:
       
        form = ProductForm(instance=upd)
        print('3')

    return render(request, 'admin_dashboard/create.html', {'form': form})

def delete(request,product_id):
    item=get_object_or_404(Products,pk=product_id).delete()
    return redirect('admin_products')

def users_view(request):
    user=User.objects.filter(Q(is_superuser=False) & Q(is_staff=False) )
    return render(request,'admin_dashboard/users.html',{'users':user})

def orders_view(request):
    order=OrderItem.objects.all()
    return render(request,'admin_dashboard/orders.html',{'orders':order})

def user_delete(request,user_id):
    item=get_object_or_404(User,pk=user_id).delete()
    return redirect('user')

def user_update(request,user_id):
    upd = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        
        form = ProductForm(request.POST, instance=upd)
        print('2')
        if form.is_valid():
            
            form.save()
            
            return redirect('admin_products')
    else:
       
        form =UserForm(instance=upd)
    
    return render(request,'admin_dashboard/user_update.html',{'form':form})
    



def dashboard(request) :
    products_count=Products.objects.all().count()
    user_count=User.objects.filter(Q(is_superuser=False) & Q(is_staff=False) ).count()
    orders_count=OrderItem.objects.all().count()
    orders_items = OrderItem.objects.all()
    total_revenue = sum(item.item_subtotal for item in orders_items)

    context={
        'products_count':products_count,
        'user_count':user_count,
        'orders_count':orders_count,
        'total_revenue' : total_revenue,
    }
    return render(request,'admin_dashboard/dashboard.html',{'context':context})



def create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        print('hello')
        if form.is_valid():
            form.save()
            print('if')
            messages.success(request, 'Product successfully created!')
            return redirect('admin_products')
        else:
            messages.error(request, 'Form submission failed. Please correct the errors below.')
            print(form.errors)

    else:
        form = ProductForm()

    return render(request, 'admin_dashboard/create.html', {'form': form})
