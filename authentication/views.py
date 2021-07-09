from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions, status, generics, response
from .serializers import *
from .validators import *
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action, api_view
from rest_framework import permissions
from django.contrib.auth import get_user_model
from .tokens import *
from django.db import transaction

from .utils import *
from .constants import *

User = get_user_model()

email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'


class ObtainTokenPairView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer


class SignUp(APIView):
    # parser_classes = (MultiPartParser,)
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        method='post',
        manual_parameters=[
            openapi.Parameter(
                name='first_name', in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="First Name"
            ),
            openapi.Parameter(
                name='last_name', in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="Last Name"
            ),
            openapi.Parameter(
                name='username', in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="Username"
            ),
            openapi.Parameter(
                name='email', in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="Email"
            ),
            openapi.Parameter(
                name='password', in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="Password"
            )
        ],
        tags=['auth'],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Sucess"
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Unauthorized"
            ),
        }
    )
    @action(methods=['post'], detail=False, permission_classes=[],
            url_path='', url_name='')
    def post(self, request, format='json'):
        try:
            with transaction.atomic():
                validator = SignUpValidator(data=request.data)
                if validator.is_valid():
                    validated_data = validator.validated_data
                    if validated_data['should_verify']:
                        email = request.data['email']
                        user = User.objects.get(email=email)
                        return response.Response({'should_verify': True,
                                         'user_id': user.id}, status=status.HTTP_200_OK)
                    user = User(
                        first_name=validated_data['first_name'],
                        last_name=validated_data['last_name'],
                        email=validated_data['email'],
                        function=validated_data['function'],
                        quality=validated_data['quality'],
                        role=validated_data['role'],
                        sex=validated_data['sex'],
                        username=validated_data['username'],
                    )
                    user.set_password(validated_data['password'])
                    user.save()

                    user = registered_user(data=validated_data)
                    send_signup_verificaion_mail(user=user, request=request)
                    return response.Response(
                        {"message": "Please confirm your email address to complete the registration",
                         "user_id": user.id
                         }, status=status.HTTP_201_CREATED)
                else:
                    return response.Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return response.Response('Exception: {}'.format(error), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Login(APIView):

    permission_classes = (permissions.AllowAny,)
    # parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        method='post',
        manual_parameters=[
            openapi.Parameter(
                name='login_text', in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="username or email"
            ),
            openapi.Parameter(
                name='password', in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="password"
            )
        ],
        tags=['auth'],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Success"
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Unauthorized"
            ),
        }
    )
    @action(methods=['post'], detail=False, permission_classes=[],)
    def post(self, request, format='json'):
        validator = LoginValidator(data=request.data)
        if validator.is_valid():
            validated_data = validator.validated_data
            if validated_data['should_verify']:
                user_id = validated_data['user_id']
                return response.Response({'should_verify': True, 'user_id': user_id}, status=status.HTTP_200_OK)
            username = validated_data['username']
            password = validated_data['password']
            auth_user = authenticate(username=username, password=password)
            if auth_user is not None:
                return response.Response(get_tokens_plus_user(auth_user, request), status=status.HTTP_200_OK)
            else:
                return response.Response({'message': "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return response.Response({'message': "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)



