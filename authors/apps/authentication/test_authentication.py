import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import APITestCase, APIClient
from .models import UserManager


class TestUsers(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def generate_user(self, username='', email='',password=''):
        user = {
            'user':{
            'email': email,
            'username': username,
            'password': password
            }
        }
        return user
    def create_user(self, username='', email='',password=''):
        user = self.generate_user(username, email,password)
        self.client.post('/api/users/', user, format='json')
        return user

    def test_user_registration(self):
        user = self.generate_user('athena', 'athena@gmail.com', 'password@user')
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
        login_details= self.generate_user('','athena@gmail.com', 'password@user')
        response = self.client.post('/api/users/login/',login_details, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            json.loads(response.content),
            {"user": {"email": "athena@gmail.com", "username": "athena"}}
        )
    