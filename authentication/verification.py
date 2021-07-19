from .models import *
from django.utils import timezone
from .utils import *
import pyotp
from .tokens import *
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import permissions, viewsets, permissions, status, generics
from rest_framework.decorators import action
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from .validators import *
from .serializers import *
from django.shortcuts import render


from .constants import *
import django
django.setup()


User = get_user_model()


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id


class SignUpViewset(viewsets.ViewSet):
    serializer_class = None

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                name='code', in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Code",
                required=True
            ),
            openapi.Parameter(
                name='user_id', in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="User Id",
                required=True
            ),
        ],
        tags=['Activate Account'],
        operation_summary="Activate account (after sign up)",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Success"
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Unauthorized"
            ),
        },
    )
    @action(methods=['get'], detail=False, permission_classes=[],
            url_path='activate', url_name='activate')
    def verify_signup(self, request, format='json'):
        validator = SignUpVerificationValidator(data=request.query_params)
        if not validator.is_valid():
            return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)
        validated_data = validator.validated_data
        code = validated_data['code']
        user_id = int(validated_data['user_id'])

        confirm_token = ConfirmToken.objects.get(
            user__id=user_id, kind=SIGNUP_TOKEN)

        user = User.objects.get(id=int(user_id))
        date_time = confirm_token.token_epires_at
        key = confirm_token.token_hash
        if (timezone.now() < date_time):
            counter = int(user.id)
            hotp = pyotp.HOTP(key)
            if int(code) == int(hotp.at(counter)):
                user.is_active = True
                user.save()
                confirm_token.delete()
                data = get_tokens_plus_user(user , request)
                data["message"] = "Account Activated Successfully"
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({
                    "message": "Invalid Code"
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "message": "Code Expired"
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                name='email', in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Email",
                required=True
            ),
        ],
        tags=['Activate Account'],
        operation_summary="Resend Code To Activate Account",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Success"
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Unauthorized"
            ),
        }
    )
    @action(methods=['get'], detail=False, permission_classes=[],
            url_path='resend', url_name='resend')
    def resend_signup_code(self, request, format='json'):
        validator = SignUpResendValidator(data=request.query_params)
        if not validator.is_valid():
            return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)
        validated_data = validator.validated_data
        email = validated_data['email']
        user = User.objects.get(email=email)
        send_signup_verificaion_mail(user=user, request=request)
        return Response({
            "message": "Code resent succssfully!. Please check your email"
        }, status=status.HTTP_200_OK)


class PasswordResetViewset(viewsets.ViewSet):
    serializer_class = None

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                name='email', in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Email",
                required=True
            ),
        ],
        tags=['Reset Password'],
        operation_summary="Request Change of Password",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Success"
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Unauthorized"
            ),
        }
    )
    @action(methods=['get'], detail=False, permission_classes=[],
            url_path='request_change', url_name='request_change')
    def request_reset_password(self, request, format='json'):
        validator = RequestResetPasswordValidator(data=request.query_params)
        if not validator.is_valid():
            return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)
        validated_data = validator.validated_data
        email = validated_data['email']
        user = User.objects.get(email=email)
        send_password_reset_mail(user=user, request=request)
        return Response({
            "message": "Validation Code Sent!. Please check your email"
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='put',
        manual_parameters=[
            openapi.Parameter(
                name='email', in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Email",
                required=True
            ),
            openapi.Parameter(
                name='code', in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Code",
                required=True
            ),
            openapi.Parameter(
                name='password', in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="New Password",
                required=True
            ),
        ],
        tags=['Reset Password'],
        operation_summary="Reset (change) Password",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Success"
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Unauthorized"
            ),
        }
    )
    @action(methods=['put'], detail=False, permission_classes=[],
            url_path='reset', url_name='reset')
    def reset_password(self, request, format='json'):
        validator = ResetPasswordValidator(data=request.query_params)
        if not validator.is_valid():
            return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)
        validated_data = validator.validated_data

        user_id = validated_data['user_id']
        user = User.objects.get(id=user_id)
        code = validated_data['code']
        password = validated_data['password']

        confirm_token = ConfirmToken.objects.get(
            user__id=user_id, kind=PASSWORD_TOKEN)
        date_time = confirm_token.token_epires_at
        key = confirm_token.token_hash
        if (timezone.now() < date_time):
            counter = int(user.id)

            hotp = pyotp.HOTP(key)

            if int(code) == int(hotp.at(counter)):
                user.set_password(password)
                user.save()
                confirm_token.delete()
                return Response({
                    "message": "Password Resetted Successfully"
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "message": "Invalid Code"
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "message": "Code Expired"
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Code resent succssfully!. Please check your email"
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                name='email', in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Email",
                required=True
            ),
        ],
        tags=['Reset Password'],
        operation_summary="Resend Password change (reset) Code",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Success"
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Unauthorized"
            ),
        }
    )
    @action(methods=['get'], detail=False, permission_classes=[],
            url_path='resend', url_name='resend')
    def resend_password_reset_code(self, request, format='json'):
        validator = RequestResetPasswordValidator(data=request.query_params)
        if not validator.is_valid():
            return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)
        validated_data = validator.validated_data
        email = validated_data['email']
        user = User.objects.get(email=email)
        send_password_reset_mail(user=user, request=request)
        return Response({
            "message": "Code resent succssfully!. Please check your email"
        }, status=status.HTTP_200_OK)


class ChangeEmailViewset(viewsets.ViewSet):
    serializer_class = None

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                name='new_email', in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="New Email",
                required=True
            ),
            openapi.Parameter(
                name='user_id', in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="User Id",
                required=True
            ),
        ],
        tags=['Change Email'],
        operation_summary="Request Change Email",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Success"
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Unauthorized"
            ),
        }
    )
    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated, IsOwner],
            url_path='request', url_name='request')
    def request_email_change(self, request, format='json'):
        validator = RequestChangeEmailValidator(data=request.query_params)
        if not validator.is_valid():
            return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)
        if validator.is_valid():
            validated_data = validator.validated_data
            new_email = validated_data['new_email']
            user_id = validated_data['user_id']
            user = User.objects.get(id=user_id)

            # Ensure that the request user is same as the owner of the account
            self.check_object_permissions(request, user)

            send_change_email_code(user=user, email=new_email)
            return Response({
                "message": "Code sent successfully!. Please check your email"
            }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                name='code', in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Code",
                required=True
            ),
            openapi.Parameter(
                name='user_id', in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="User Id",
                required=True
            ),
        ],
        tags=['Change Email'],
        operation_summary="Confirm Email Change",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Success"
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Unauthorized"
            ),
        }
    )
    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated, IsOwner],
            url_path='confirm', url_name='confirm')
    def confirm_email_change(self, request, format='json'):
        validator = ConfirmChangeEmailValidator(data=request.query_params)
        if not validator.is_valid():
            return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)
        if validator.is_valid():
            validated_data = validator.validated_data

            user_id = validated_data['user_id']
            user = User.objects.get(id=user_id)

            # Ensure that the request user is same as the owner of the account
            self.check_object_permissions(request, user)

            code = validated_data['code']

            confirm_token = ConfirmToken.objects.get(
                user__id=user_id, kind=EMAIL_TOKEN)
            date_time = confirm_token.token_epires_at
            key = confirm_token.token_hash
            new_email = confirm_token.extra_data
            if (timezone.now() < date_time):
                counter = int(user.id)

                hotp = pyotp.HOTP(key)
                if int(code) == int(hotp.at(counter)):
                    user.email = new_email
                    user.save()
                    confirm_token.delete()
                    return Response({
                        "message": "Email changed Successfully"
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "message": "Invalid Code"
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "message": "Code Expired"
                }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                name='new_email', in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="New Email",
                required=True
            ),
            openapi.Parameter(
                name='user_id', in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="User Id",
                required=True
            ),
        ],
        tags=['Change Email'],
        operation_summary="Resend Email change Code",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Success"
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Unauthorized"
            ),
        }
    )
    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated, IsOwner],
            url_path='resend', url_name='resend')
    def resend_change_email_code(self, request, format='json'):
        validator = RequestChangeEmailValidator(data=request.query_params)
        if not validator.is_valid():
            return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)
        if validator.is_valid():
            validated_data = validator.validated_data
            new_email = validated_data['new_email']
            user_id = validated_data['user_id']
            user = User.objects.get(id=user_id)

            # Ensure that the request user is same as the owner of the account
            self.check_object_permissions(request, user)

            send_change_email_code(user=user, email=new_email)
            return Response({
                "message": "Code resent successfully!. Please check your email"
            }, status=status.HTTP_200_OK)
