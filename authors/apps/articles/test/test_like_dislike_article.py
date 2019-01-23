import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from ..models import Profile
from ...authentication.models import User
from ...authentication.views import VerifyAccount, RegistrationAPIView


class TestLike(APITestCase):

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

    def create_testing_article(self):
        article = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
                "images": [{"image_url": "http://www.andela.com",
                            "image_description": "jsjjsjs"
                            }]
            }
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        response = self.client.post(
            '/api/articles/', article, format='json')
        slug = response.data['slug']
        return slug

    def test_like_existing_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        slug = self.create_testing_article()
        url = '/api/articles/'+slug+'/like/'
        response = self.client.post(str(url), format='json')
        response = self.client.post(str(url), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['article']['slug'],
            slug
        )
        self.assertEqual(
            response.data['like'],
            True
        )
    def test_return_positive_like_status_of_an_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        slug = self.create_testing_article()
        url = '/api/articles/'+slug+'/like/'
        response = self.client.post(str(url), format='json')
        response = self.client.post(str(url), format='json')
        url2 = '/api/articles/'+slug
        response2 = self.client.get(str(url2), format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['like'],
            True
        )

    def test_return_negative_like_status_of_an_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        slug = self.create_testing_article()
        url = '/api/articles/'+slug+'/like/'
        response = self.client.post(str(url), format='json')
        response = self.client.delete(str(url), format='json')
        url2 = '/api/articles/'+slug
        response2 = self.client.get(str(url2), format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['like'],
            False
        )

    def test_like_then_dislike_existing_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        slug = self.create_testing_article()
        url = '/api/articles/'+slug+'/like/'
        response = self.client.post(str(url), format='json')
        response = self.client.delete(str(url), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['article']['slug'],
            slug
        )
        self.assertEqual(
            response.data['like'],
            False
        )

    def test_like_then_dislike_then_like_existing_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        slug = self.create_testing_article()
        url = '/api/articles/'+slug+'/like/'
        response = self.client.post(str(url), format='json')
        response = self.client.delete(str(url), format='json')
        response = self.client.post(str(url), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['article']['slug'],
            slug
        )
        self.assertEqual(
            response.data['like'],
            True
        )

    def test_like_non_existing_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        slug = "non_existing_slug"
        url = '/api/articles/'+slug+'/like/'
        response = self.client.post(str(url), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data['detail'],
            'This artical doesnot exist'
        )

    def test_dislike_existing_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        slug = self.create_testing_article()
        url = '/api/articles/'+slug+'/like/'
        response = self.client.delete(str(url), format='json')
        response = self.client.delete(str(url), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['article']['slug'],
            slug
        )
        self.assertEqual(
            response.data['like'],
            False
        )

    def test_dislike_non_existing_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        slug = "non_existing_slug"
        url = '/api/articles/'+slug+'/like/'
        response = self.client.delete(str(url), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data['detail'],
            'This artical doesnot exist'
        )
