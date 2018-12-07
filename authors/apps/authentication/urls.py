from django.conf.urls import url
from django.urls import path, include

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView,
    PasswordResetView, PasswordResetConfirmView,
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
    path('password_reset/', PasswordResetView.as_view()),
    path('password_reset_confirm/<slug>', PasswordResetConfirmView.as_view()),
]
