from .serializers import CustomUserSerializer
from .constants import *
from .models import *
import string
import random
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken
import base64
import pyotp
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.conf import settings
import datetime
import django
django.setup()



User = get_user_model()

email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'


def get_random_str(n):

    # printing lowercase
    letters = string.ascii_lowercase + string.digits + string.ascii_uppercase
    random_str = ''.join(random.choice(letters) for i in range(n))
    return random_str


class generateKey:
    @ staticmethod
    def returnValue():
        return str(datetime.datetime.date(datetime.datetime.now())) + get_random_str(30)


def get_key():
    keygen = generateKey()
    key = base64.b32encode(keygen.returnValue().encode())
    return key


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def get_tokens_plus_user(user, request=None):
    refresh = RefreshToken.for_user(user)
    serializer = CustomUserSerializer(
        instance=user, context={"request": request})
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': serializer.data,
    }


def registered_user(data):
    """
    register user during signup
    """
    user = User.objects.get(username=data['username'])
    user.is_active = False
    user.save()
    return user


def send_signup_verificaion_mail(user, request):
    """
    Send email verificaion during signup
    """
    try:
        # generate code
        key = get_key()
        hotp = pyotp.HOTP(key)
        counter = int(user.id)
        code = hotp.at(counter)
        print(code)
        # update code expiration
        date_time = datetime.datetime.now() + datetime.timedelta(minutes=settings.SIGN_UP_LIMIT)
        confirm_token = ConfirmToken(
            user=user,
            kind=SIGNUP_TOKEN,
            token_hash=key,
            token_epires_at=date_time
        )
        confirm_token.save()
        mail_subject = 'Activate your account.'
        to_email = user.email
        # message = '<div>Hi '+ '<h4 style="font-weight:bold">user.username</h4>'  +' Thanks for using Interconnex. <br>This is your Signup Verification Code!<br><h3>Code: <strong>'+code+'</strong></h3></div>'

        message = render_to_string('mail/account_active_email.html', {
            'user': user,
            'code': code,
        })
        email = EmailMessage(
            mail_subject, message, from_email=settings.EMAIL_HOST_USER, to=[to_email]
        )
        # set type to html
        email.content_subtype = "html"
        email.send()
    except Exception as e:
        print(".................... COULD NOT SEND CODE >>>>>>>>>>>>>>>>>>>>>")
        print(e)


def send_password_reset_mail(user, request):
    """
    Send email verificaion during signup
    """
    try:
        # generate code
        key = get_key()
        hotp = pyotp.HOTP(key)
        counter = int(user.id)
        code = hotp.at(counter)

        # update code expiration
        date_time = datetime.datetime.now() + datetime.timedelta(minutes=settings.SIGN_UP_LIMIT)
        confirm_token = ConfirmToken(
            user=user,
            kind=PASSWORD_TOKEN,
            token_hash=key,
            token_epires_at=date_time
        )
        confirm_token.save()
        #
        mail_subject = 'Reset Your Password'
        # message = '<div>Hi '+ '<h4 style="font-weight:bold">user.username</h4>'  +' Thanks for using Interconnex. <br>This is the code for resetting your password!<br><h3>Code: <strong>'+code+'</strong></h3></div>'

        message = render_to_string('mail/reset_password.html', {
            'user': user,
            'code': code,
        })
        to_email = user.email
        email = EmailMessage(
            mail_subject, message,from_email=settings.EMAIL_HOST_USER, to=[to_email]
        )
        # set type to html
        email.content_subtype = "html"
        email.send()
    except Exception as e:
        print(".................... COULD NOT SEND CODE >>>>>>>>>>>>>>>>>>>>>")
        print(e)


def send_change_email_code(user, email):
    """
    Send 'Change Email' Code
    """
    try:
        # generate code
        key = get_key()
        hotp = pyotp.HOTP(key)
        counter = int(user.id)
        code = hotp.at(counter)

        # update code expiration
        date_time = datetime.datetime.now() + datetime.timedelta(minutes=settings.SIGN_UP_LIMIT)
        confirm_token = ConfirmToken(
            user=user,
            kind=EMAIL_TOKEN,
            token_hash=key,
            token_epires_at=date_time,
            extra_data=email
        )
        confirm_token.save()
        #
        mail_subject = 'Change Your Email'
        # message = '<div>Hi '+ '<h4 style="font-weight:bold">user.username</h4>'  +' Thanks for using Interconnex. <br>This is the code for Changing Your Email!<br><h3>Code: <strong>'+code+'</strong></h3></div>'
        message = render_to_string('mail/change_email.html', {
            'user': user,
            'code': code,
        })
        to_email = email
        email = EmailMessage(
            mail_subject, message,from_email=settings.EMAIL_HOST_USER, to=[to_email]
        )
        # set type to html
        email.content_subtype = "html"
        email.send()
    except Exception as e:
        print(".................... COULD NOT SEND CODE >>>>>>>>>>>>>>>>>>>>>")
        print(e)
