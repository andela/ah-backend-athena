import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory

from ..serializers import LoginSerializer
from rest_framework.exceptions import ValidationError
from ..views import VerifyAccount, RegistrationAPIView
from ..models import UserManager, User


class TestUsers(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def generate_user(self, username='', email='', password=''):
        user = {
            'user': {
                'email': email,
                'username': username,
                'password': password
            }
        }
        return user

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

    def create_user(self, username='', email='', password=''):
        user = self.generate_user(username, email, password)
        self.client.post('/api/users/', user, format='json')
        return user

    def test_user_registration(self):
        user = self.generate_user(
            'athena', 'athena@gmail.com', 'P1assword@user')
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            json.loads(
                response.content), {
                "user": {
                    "message": "A verification email has been sent to athena@gmail.com"}})

    def test_cannot_login_without_verification(self):
        self.create_user('athena', 'athena@gmail.com', 'P1assword@user')
        login_details = self.generate_user(
            '', 'athena@gmail.com', 'P1assword@user')
        response = self.client.post(
            '/api/users/login/', login_details, format='json')
        self.assertEqual(
            json.loads(
                response.content), {
                "errors": {
                    "error": ["Your email is not verified, Please check your email for a verification link"]}})

    def test_user_registration_empty_details(self):
        user = self.generate_user('', '', '')
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_wrong_email_format(self):
        user = self.generate_user('athena', 'athenmail', 'P1assword@user')
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        self.create_user('athena', 'athena@gmail.com', '1Password@user')
        login_details = self.generate_user(
            '', 'athena@gmail.com', '1Password@user')
        request = APIRequestFactory().post(
            reverse("registration")
        )
        user = User.objects.get()
        token, uidb64 = RegistrationAPIView.generate_activation_link(
            user, request, send=False)
        self.verify_account(token, uidb64)
        response = self.client.post(
            '/api/users/login/', login_details, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            json.loads(response.content),
            {"user": {
                "email": "athena@gmail.com",
                "username": "athena",
                'token': response.data['token']
            }
            }
        )

    def test_unauthorized_access_to_authenticated_endpoint(self):
        self.create_user('kasule', 'athena@gmail.com', 'Password@user1')
        login_details = self.generate_user(
            '', 'athena@gmail.com', 'Password@user1')
        response = self.client.post(
            '/api/user/', login_details, format='json')
        self.assertTrue(response.status_code == 403)
        self.assertEqual(
            json.loads(response.content),
            {"user": {
                "detail": "Authentication credentials were not provided."
            }
            }
        )

    def test_user_with_valid_token_access_protected_endpoints(self):
        self.create_user('soko', 'athena@gmail.com', 'Password@user1')
        login_details = self.generate_user(
            '', 'athena@gmail.com', 'Password@user1')
        request = APIRequestFactory().post(
            reverse("registration")
        )
        user = User.objects.get()
        token, uidb64 = RegistrationAPIView.generate_activation_link(
            user, request, send=False)
        self.verify_account(token, uidb64)
        response = self.client.post(
            '/api/users/login/', login_details, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        res = self.client.get(
            '/api/user/', login_details, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            json.loads(res.content),
            {"user": {
                "email": "athena@gmail.com",
                "username": "soko",
                'token': res.data['token']
            }
            }
        )

    def test_invalid_token(self):
        self.create_user('josh', 'athena@gmail.com', 'Password@user1')
        login_details = self.generate_user(
            '', 'athena@gmail.com', 'Password@user1')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + '123hjhj12')
        res = self.client.get(
            '/api/user/', login_details, format='json')
        self.assertTrue(res.status_code == 401)
        self.assertEqual(
            'Invalid token. please login again', res.data['detail'])

    def test_login_jwt_with_bad_credentials(self):
        self.create_user('kica', 'athena@gmail.com', 'Password@user11')
        login_details = self.generate_user(
            '', 'kica@gmail.com', 'Password@user11')
        response = self.client.post(
            '/api/users/login/', login_details, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"errors": {
                "error": [
                    "A user with this email and password was not found."]
            }
            },
            json.loads(response.content))

    def test_email_is_required(self):
        data = {
            "email": None,
            "password": "Password1"
        }
        with self.assertRaises(ValidationError) as email_error:
            LoginSerializer().validate(data)
        exce = email_error.exception
        self.assertIn('An email address is required to log in', str(exce))

    def test_password_is_required(self):
        data = {
            "email": 'athena@gmail.com',
            "password": None
        }
        with self.assertRaises(ValidationError) as pass_error:
            LoginSerializer().validate(data)
        exce = pass_error.exception
        self.assertIn('A password is required to log in.', str(exce))
