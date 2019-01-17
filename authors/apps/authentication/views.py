from .serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserSerializer,
    GoogleAuthSerializer,
    FacebookAuthSerializer,
    TwitterAuthSerializer,
)
from .renderers import UserJSONRenderer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site

from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer
)
from ..profiles.models import Profile
from .renderers import UserJSONRenderer

from .models import User
from django.utils.http import force_bytes
from django.contrib.auth.hashers import make_password
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer
)

from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.core.signing import TimestampSigner
from django.shortcuts import redirect
import os


class RegistrationAPIView(GenericAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        address = serializer.data['email']
        user = User.objects.filter(email=user['email']).first()
        

        RegistrationAPIView.generate_activation_link(user, request)
        return Response({"message": "A verification email has been sent to {}".format(
            address)}, status=status.HTTP_201_CREATED)

    @staticmethod
    def generate_activation_link(user, request=None, send=True):
        """
        This method creates a custom actvation link that will be used when verifying
        a user's email containing a token and a unique id. The generated token bares the user's identity
        and the unique id is just an encoded byte string of the user's username

        """
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(
            force_bytes(user.username)).decode()
        domain = 'https://{}'.format(get_current_site(request))
        subject = 'Author\'s Heaven account email verification'
        route = "api/activate"
        url = "{}/{}/{}/{}/".format(domain, route, token, uidb64)
        message = 'Please follow the following link to activate your account \n {}'.format(
            url)
        from_email = settings.EMAIL_HOST_USER
        to_list = [user.email]
        if send:
            send_mail(
                subject=subject,
                from_email=from_email,
                recipient_list=to_list,
                message=message,
                fail_silently=False)

        return token, uidb64


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


class GoogleAuthAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = GoogleAuthSerializer

    def post(self, request):
        token = request.data.get('token', {})
        serializer = self.serializer_class(data={'auth_token': token})
        serializer.is_valid(raise_exception=True)
        res = {"jwt_token": serializer.data['auth_token']}
        return Response(res, status=status.HTTP_200_OK)


class FacebookAuthAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = FacebookAuthSerializer

    def post(self, request):
        token = request.data.get('token', {})
        serializer = self.serializer_class(data={'auth_token': token})
        serializer.is_valid(raise_exception=True)
        res = {"jwt_token": serializer.data['auth_token']}
        return Response(res, status=status.HTTP_200_OK)


class TwitterAuthAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = TwitterAuthSerializer

    def post(self, request):
        token = request.data.get('token', {})
        serializer = self.serializer_class(data={'auth_token': token})
        serializer.is_valid(raise_exception=True)
        res = {"jwt_token": serializer.data['auth_token']}
        return Response(res, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
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

        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        bio = serializer_data.get('bio', request.user.profile.bio)
        image = serializer_data.get('image', request.user.profile.image)

        # gets loggedin user id and gets profile object of the user and updates profile
        user_id = User.objects.all().filter(
            email=request.user).values()[0]['id']
        profile = Profile.objects.get(user__id=user_id)
        profile.bio = bio
        profile.image = image
        profile.save()

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

        send_mail(subject, message, email_from,
                  recipient_list, fail_silently=False)

        res = {"message": "An email has been to this email"}
        return Response(res, status.HTTP_200_OK)


class PasswordResetConfirmView(RetrieveUpdateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetConfirmSerializer

    def get(self, request, **kwargs):
        front_end_domain = os.getenv(
            "FRONT_END_DOMAIN", "http://localhost:3000/")

        slug = kwargs['slug'].split('-')[2]
        try:
            username = PasswordResetView().decode_id(slug)
            User.objects.get(username=username)
        except:
            return redirect(front_end_domain+"invalid_link")
        return redirect(front_end_domain+"password_reset_confirm/"+kwargs['slug'])

    def update(self, request, **kwargs):
        serializer_data = request.data
        slug = kwargs['slug'].split('-')[2]
        try:
            user = PasswordResetView().decode_id(slug)
        except:
            return Response({
                "error": {
                    "detail": [
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
                "message": {
                    "detail": [
                        "Password successfully reset"
                    ]
                }
            }, status=status.HTTP_200_OK)
        return Response({
            "errors": {
                "body": [
                    "passwords do not match"
                ]
            }
        }, status=status.HTTP_400_BAD_REQUEST)


class VerifyAccount(GenericAPIView):

    def get(self, request, token, uidb64):
        """
        Here, I am verifying both the token and encoded byte string embeded in the activation link
        by checking the token against the bearer username and also the encoded byte string

        """
        front_end_domain = os.getenv(
            "FRONT_END_DOMAIN", "http://localhost:3000/")

        username = force_text(urlsafe_base64_decode(uidb64))

        user = User.objects.filter(username=username).first()
        validate_token = default_token_generator.check_token(user, token)

        data = {"message": "Your account has been verified, You can login now!"}
        stat = status.HTTP_200_OK

        if not validate_token:
            data['message'] = "Your activation link is Invalid or has expired."
            stat = status.HTTP_400_BAD_REQUEST
            return redirect(front_end_domain+"invalid_link")

        else:
            user.is_verified = True
            user.save()

        return redirect(front_end_domain+"login")
