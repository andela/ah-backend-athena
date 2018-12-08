import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import APITestCase, APIClient
from ..models import Profile


class TestProfileCreate(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = {
            'user': {
                'email': "soko@gmail.com",
                'username': "soko",
                'password': 'sokosoko'
            }
        }

    def create_testing_user(self):
        self.client.post('/api/users/', self.user, format='json')
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        token = response.data['token']
        return token

    def test_get_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        response = self.client.get('/api/profiles/soko')
        self.assertEqual(
            json.loads(response.content)['profile']['username'],
            "soko"
        )

    def test_get_non_existing_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        response = self.client.get('/api/profiles/sokop')
        self.assertEqual(
            json.loads(response.content)['profile']['detail'],
            "Profile does not exist."
        )

    def test_update_profile(self):
        data = {
                "user":{
                    "email": "kool@andela.com",
                    "bio": "I love andela",
                    "image": "http://andela.com/paul.jpg"
                }
                }

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        self.client.put(
            '/api/user/', data, format='json')
        response = self.client.get('/api/profiles/soko')
        self.assertEqual(
            json.loads(response.content)['profile']['bio'],
            "I love andela"
        )


   

