from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags
from django.template.loader import render_to_string




User=get_user_model()

def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    verification_link = request.build_absolute_uri(
        reverse('verify-email', kwargs={'uidb64': uid, 'token': token})  
    )

    subject = 'Verify Your Email'
    message = f'Click the link below to verify your email:\n\n{verification_link}'
    send_mail(subject, message, 'your-email@gmail.com', [user.email])


def verify_email(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        user=get_object_or_404(User,pk=uid)
    except (TypeError,ValueError,OverflowError):
        return HttpResponse('invalid token')
    if default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        return HttpResponse('Email verified succesfully')
    else:
        return HttpResponse('invalid or expired verification')
    
    
    # ORDER SUCCESFULL IMAGE


# def after_order_email(request):
#     subject="Order Confirmation"
#     html_message=render_to_string('order_confirmation_email.html',{
#         'user':request.user,
#         'order'
#     })
    
    