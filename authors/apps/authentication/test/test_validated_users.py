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
            {'user':
                {'message': 'A verification email has been sent to athena@gmail.com'}
             })

    def test_user_registration_weak_password(self):
        user = self.generate_user(self.username, self.email, 'weakpassword')
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content)['errors']['password'],
            ['Password must contain atleast one number and a capital letter'])

    def test_user_registration_username_long(self):
        username = 'x'*300
        user = self.generate_user(username, self.email, self.password)
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content)['errors']['username'],
            ['User names must be between 3 and 10 characters'])

    def test_user_registration_username_short(self):
        username = 'x'
        user = self.generate_user(username, self.email, self.password)
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content)['errors']['username'],
            ['User names must be between 3 and 10 characters'])

    def test_user_registration_invalid_user_name(self):
        user = self.generate_user('()*&^%$#@', self.email, self.password)
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content)['errors']['username'],
            ['User names must be characters, letters and underscores only'])

    def test_user_registration_empty_credentials(self):
        user = self.generate_user('', '', '')
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content)['errors']['username'],
            ['This field may not be blank.'])

    def test_user_registration_password_long(self):
        password = 'Password@1'+'x'*300
        user = self.generate_user(self.username, self.email, password)
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content)['errors']['password'],
            ['Passwords must be between 8 to 128 characters'])

    def test_user_registration_short(self):
        password = 'Pas12'
        user = self.generate_user(self.username, self.email, password)
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content)['errors']['password'],
            ['Passwords must be between 8 to 128 characters'])
