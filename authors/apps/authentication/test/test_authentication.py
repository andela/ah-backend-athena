import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import APITestCase, APIClient
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

    def create_user(self, username='', email='', password=''):
        user = self.generate_user(username, email, password)
        self.client.post('/api/users/', user, format='json')
        return user

    def test_user_registration(self):
        user = self.generate_user(
            'athena', 'athena@gmail.com', 'password@user')
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            json.loads(response.content),
            {"user": {"email": "athena@gmail.com", "username": "athena"}}
        )

    def test_user_registration_empty_details(self):
        user = self.generate_user('', '', '')
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_wrong_email_format(self):
        user = self.generate_user('athena', 'athenmail', 'password@user')
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        self.create_user('athena', 'athena@gmail.com', 'password@user')
        login_details = self.generate_user(
            '', 'athena@gmail.com', 'password@user')
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
