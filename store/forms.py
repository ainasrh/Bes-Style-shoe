from django import forms
from .models import *

class Register_form(forms.Form):
    name=forms.CharField(max_length=100,required=True)
    email=forms.EmailField(required=True,label='Email')
    password=forms.CharField(widget=forms.PasswordInput,label='password')
    confirm_password=forms.CharField(widget=forms.PasswordInput,label='Confirm Password')

class login_form(forms.Form):
    name=forms.CharField(max_length=100,required=True)    
    password=forms.CharField(widget=forms.PasswordInput,label='password')

class ProductForm(forms.ModelForm):

    class Meta:
        model=Products
        fields='__all__'

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['id','username','email']
    
