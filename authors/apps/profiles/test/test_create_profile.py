import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from ..models import Profile
from ...authentication.models import User
from ...authentication.views import VerifyAccount, RegistrationAPIView


class TestProfileCreate(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = {
            'user': {
                'email': "soko@gmail.com",
                'username': "soko",
                'password': 'Sokosok1!'
            }
        }
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

    def create_testing_user(self):
        self.client.post('/api/users/', self.user, format='json')
        request = APIRequestFactory().post(
            reverse("registration")
        )
        user = User.objects.get()
        token, uidb64 = RegistrationAPIView.generate_activation_link(
            user, request, send=False)
        self.verify_account(token, uidb64)
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        token = response.data['token']
        return token

    def test_get_profile(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        response = self.client.get('/api/profiles/soko')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            json.loads(response.content)['profile']['username'],
            "soko"
        )

    def test_get_non_existing_profile(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        response = self.client.get('/api/profiles/sokop')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content)['profile']['detail'],
            "Profile does not exist."
        )

    def test_update_profile(self):
        data = {
            "user": {
                "email": "kool@andela.com",
                "bio": "I love andela",
                "image": "http://andela.com/paul.jpg"
            }
        }

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        self.client.put(
            '/api/user/', data, format='json')
        response = self.client.get('/api/profiles/soko')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            json.loads(response.content)['profile']['bio'],
            "I love andela"
        )
