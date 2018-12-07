from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer
)
from .renderers import UserJSONRenderer
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from .models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import (
    urlsafe_base64_decode, urlsafe_base64_encode, force_bytes,
)
from django.contrib.auth.hashers import make_password
from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer
)
from django.contrib.sites.shortcuts import get_current_site

from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.core.signing import TimestampSigner

class RegistrationAPIView(GenericAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetSerializer
    
    @classmethod
    def decode_id(self, uid):
        username = urlsafe_base64_decode(uid).decode('utf-8')
        return username

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email=user['email']).first()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.username)).decode('utf-8')
        domain = 'http://{}'.format(get_current_site(request))
        route = 'api/password_reset_confirm/'
        url = '{}/{}{}-{}'.format(domain, route, token, uid)
        subject = 'Author\'s Haven Password Reset'
        message = 'Follow this link to reset password {}'.format(url)
        email_from = settings.EMAIL_HOST_USER
        to_mail = user.email
        recipient_list = [to_mail]

        send_mail(subject, message, email_from, recipient_list, fail_silently=False)

        res = {"message":"An email has been to this email"}
        return Response(res, status.HTTP_200_OK)

class PasswordResetConfirmView(RetrieveUpdateAPIView):
    permission_classes = (AllowAny,)
    serializer_class =PasswordResetConfirmSerializer

    def get_object(self):
        return {"password":"", "confirm_password":""}

    def update(self, request, **kwargs):
        serializer_data = request.data
        slug = kwargs['slug'].split('-')[2]
        try:
            user = PasswordResetView().decode_id(slug)
        except:
            return Response({
                "error":{
                    "detail":[
                        "Sorry, this link is invalid"
                    ]
                }
            }, status=status.HTTP_400_BAD_REQUEST) 
        
        if serializer_data['password'] == serializer_data['confirm_password']:
            serializer = self.serializer_class(
                request.data, data=serializer_data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            new_password = make_password(serializer_data['confirm_password'])
            User.objects.filter(username=user).update(password=new_password)

            return Response({
                "message":{
                    "detail":[
                        "Password successfully reset"
                    ]
                }
            }, status=status.HTTP_200_OK)
        return Response({
            "erros":{
                "body":[
                    "passwords do not match"
                ]
            }
        }, status=status.HTTP_400_BAD_REQUEST)
