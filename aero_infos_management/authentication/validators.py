from .constants import *
from .models import *
from django.conf import settings
import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q
import django
django.setup()


email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'


User = get_user_model()


class LoginValidator(serializers.Serializer):
    login_text = serializers.CharField(max_length=30, required=True)
    password = serializers.CharField(max_length=200, required=True)

    def validate(self, data):
        login_text = data['login_text']
        is_email = re.search(email_regex, login_text)
        data['should_verify'] = False
        if is_email:
            try:
                user = User.objects.get(email=login_text)
                data['username'] = user.username
                if not user.is_active:
                    data['should_verify'] = True
                    data['user_id'] = user.id
            except:
                raise serializers.ValidationError({'login_text':
                                                   "user with such email does not exist"})
        else:
            try:
                user = User.objects.get(username=login_text)
                data['username'] = login_text
                if not user.is_active:
                    data['should_verify'] = True
                    data['user_id'] = user.id
            except:
                raise serializers.ValidationError({'login_text':
                                                   "user with such username does not exist"}
                                                  )
        return data


class SignUpValidator(serializers.Serializer):
    first_name = serializers.CharField(required=True, max_length=80)
    last_name = serializers.CharField(required=True, max_length=80)
    function = serializers.CharField(required=False, max_length=80)
    quality = serializers.CharField(required=False, max_length=80)
    sex = serializers.CharField(required=False, max_length=10)
    role = serializers.CharField(required=True, max_length=30)
    email = serializers.EmailField(max_length=200, required=True)
    username = serializers.CharField(required=True, max_length=80)
    password = serializers.CharField(
        min_length=8, write_only=True, required=True)

    def validate(self, data):
        users = User.objects.filter(
            Q(username=data['username']) | Q(email=data['email']))

        data['should_verify'] = False
        data['same_username'] = False
        data['same_email'] = False

        if len(users) > 0:
            for user in users:
                if user.username == data['username'] and user.email == data['email']:
                    data['should_verify'] = True
                if user.username == data['username'] and user.email != data['email']:
                    data['same_username'] = True
                if user.email == data['email'] and user.username != data['username']:
                    data['same_email'] = True
            if not data['should_verify']:
                if data['same_username']:
                    raise serializers.ValidationError({'username':
                                                       "Username is already taken"})
                if data['same_email']:
                    raise serializers.ValidationError({'email':
                                                       "Email is already taken", })
        return data

class SignUpVerificationValidator(serializers.Serializer):
    code = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)

    def validate(self, data):
        user_id = int(data['user_id'])
        user = User.objects.filter(id=user_id)
        if not user.exists():
            raise serializers.ValidationError({'user_id':
                                               "user with such id does not exist"})
        confirm_token = ConfirmToken.objects.filter(
            user__id=user_id, kind=SIGNUP_TOKEN)
        if not confirm_token.exists():
            raise serializers.ValidationError({'user_id':
                                               "Invalid Token"})
        return data


class SignUpResendValidator(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, data):
        email = data['email']
        user = User.objects.filter(email=email)
        if not user.exists():
            raise serializers.ValidationError({'email':
                                               "user with such email does not exist"})
        confirm_token = ConfirmToken.objects.filter(
            user__email=email, kind=SIGNUP_TOKEN)
        if confirm_token.exists():
            confirm_token[0].delete()
        return data


class RequestResetPasswordValidator(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, data):
        email = data['email']
        user = User.objects.filter(email=email)
        if not user.exists():
            raise serializers.ValidationError({'email':
                                               "user with such email does not exist"})
        confirm_token = ConfirmToken.objects.filter(
            user__email=email, kind=PASSWORD_TOKEN)
        if confirm_token.exists():
            confirm_token[0].delete()
        return data


class ResetPasswordValidator(serializers.Serializer):
    password = serializers.CharField(max_length=200, required=True)
    code = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)

    def validate(self, data):
        user_id = data['user_id']
        user = User.objects.filter(id=user_id)
        if not user.exists():
            raise serializers.ValidationError({'email':
                                               "user with such email does not exist"}
                                              )
        confirm_token = ConfirmToken.objects.filter(
            user__id=user_id, kind=PASSWORD_TOKEN)
        if not confirm_token.exists():
            raise serializers.ValidationError({'non_field_errors':
                                               "Invalid Token"}
                                              )
        return data



class RequestChangeEmailValidator(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    new_email = serializers.EmailField(required=True)

    def validate(self, data):
        new_email = data['new_email']
        user_id = int(data['user_id'])

        user_with_new_mail = User.objects.filter(email=new_email)
        if user_with_new_mail.exists():
            raise serializers.ValidationError({'new_email':
                                               "user with such email already exist"}
                                              )
        user = User.objects.filter(id=user_id)
        if not user.exists():
            raise serializers.ValidationError({'id':
                                               "user not found"}
                                              )
        confirm_token = ConfirmToken.objects.filter(
            user__id=user_id, kind=EMAIL_TOKEN)
        if confirm_token.exists():
            confirm_token[0].delete()

        return data


class ConfirmChangeEmailValidator(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    code = serializers.IntegerField(required=True)
    def validate_user_id(self, value):
        user = User.objects.filter(id=value)
        if not user.exists():
            raise serializers.ValidationError("user not found")
        return value

    def validate(self, data):
        user_id = data['user_id']
        confirm_token = ConfirmToken.objects.filter(
            user__id=user_id, kind=EMAIL_TOKEN)
        if not confirm_token.exists():
            raise serializers.ValidationError("invalid Token")

        return data

