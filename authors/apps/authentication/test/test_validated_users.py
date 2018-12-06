import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import APITestCase, APIClient
from ..models import User, UserManager


class TestUswers(APITestCase):
    """
    This class tests user registration and login with validated
    credentials
    """

    def setUp(self):
        self.client = APIClient()
        self.username = 'athena'
        self.email = 'athena@gmail.com'
        self.password = 'PasswordA123B@1'

    def tearDown(self):
        pass

    def generate_user(self, username='', email='', password=''):
        user = {
            'user': {
                'email': email,
                'username': username,
                'password': password
            }
        }
        return user

    def user_login(self, user):
        response = self.client.post('/api/users/login/', user, format='json')
        token = json.loads(response.content)['user']['token']
        return token

    @property
    def get_token(self, user):
        return self.user_login(user)

    def test_user_registration_valid_credentials(self):
        user = self.generate_user(self.username, self.email, self.password)
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            json.loads(response.content),
            {"user": {"email": "athena@gmail.com", "username": "athena"}}
        )

    def test_user_registration_weak_password(self):
        user = self.generate_user(self.username, self.email, 'weakpassword')
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            {"errors": {"email": "athena@gmail.com", "username": "athena"}},
            json.loads(response.content)['errors'][email][0]
        )

    def test_user_registration_username_long(self):
        username = 'x'*300
        user = self.generate_user(username, self.email, self.password)
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_username_short(self):
        username = 'x'
        user = self.generate_user(username, self.email, self.password)
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_user_name(self):
        user = self.generate_user('()*&^%$#@', self.email, self.password)
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_empty_credentials(self):
        user = self.generate_user('', '', '')
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
