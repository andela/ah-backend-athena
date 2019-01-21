import json
from unittest.mock import patch

from django.urls import reverse
from django.core import mail
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text

from ..models import User
from ..views import RegistrationAPIView, VerifyAccount


class VerificationTestCase(APITestCase):
    def setUp(self):
        self.data = {
            "user": {
                "username": "Ntale",
                "email": "shadik.ntale@andela.com",
                "password": "AthenaD0a"
            }
        }
        self.url = reverse('registration')
        self.client.post(self.url, self.data, format='json')
        self.request = APIRequestFactory().post(
            reverse("registration"))

    def verify_account(self, token, uidb64):
        request = APIRequestFactory().get(
            reverse(
                "activate_account",
                kwargs={
                    "token": token,
                    "uidb64": uidb64}))
        verify_account = VerifyAccount.as_view()
        response = verify_account(request, token=token, uidb64=uidb64)
        return response

    def test_sends_email(self):
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            "Author's Heaven account email verification")

    def test_account_verified(self):
        user = User.objects.get()
        req = self.request
        token, uidb64 = RegistrationAPIView.generate_activation_link(
            user, req, send=False)
        response = self.verify_account(token, uidb64)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_generate_activation_link_function(self):
        user = User.objects.get()
        request = self.request
        token, uid = RegistrationAPIView.generate_activation_link(
            user, request, send=False)
        self.assertFalse(token == None)
        self.assertFalse(uid == None)
        self.assertFalse(len(mail.outbox) == 2)

    def test_send_activation_link(self):
        with patch('authors.apps.authentication.views.send_mail') as mock_mail:
            user = User.objects.get()
            request = self.request

            RegistrationAPIView.generate_activation_link(
                user, request, send=False)
            self.assertFalse(mock_mail.called)

            token, uid = RegistrationAPIView.generate_activation_link(
                user, request, send=True)
            self.assertTrue(mock_mail.called)
            mock_mail.assert_called_with(
                subject="Author's Heaven account email verification",
                from_email="athenad0a@gmail.com",
                recipient_list=['shadik.ntale@andela.com'],
                message="Please follow the following link to activate your account \n https://testserver/api/activate/{}/{}/".format(
                    token, uid),
                fail_silently=False)

    def test_invalid_verification_link(self):
        request = self.request

        user = User.objects.get()
        token, uid = RegistrationAPIView.generate_activation_link(
            user, request, send=False)

        # create the uid from a different username
        uid = urlsafe_base64_encode(force_bytes(
            "invalid_username")).decode("utf-8")

        response = self.verify_account(token, uid)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
