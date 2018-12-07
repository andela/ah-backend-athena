from django.conf.urls import url
from django.urls import path, include

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView,
    PasswordResetView, PasswordResetConfirmView, VerifyAccount)
urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view(), name="registration"),
    path('users/login/', LoginAPIView.as_view()),
    path('password_reset/', PasswordResetView.as_view()),
    path('password_reset_confirm/<slug>', PasswordResetConfirmView.as_view()),
    path('activate/<token>/<uidb64>/', VerifyAccount.as_view(), name="activate_account"),
]
