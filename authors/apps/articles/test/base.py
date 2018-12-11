from django.test import TestCase

import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import (
    APITestCase,
    APIClient,
    APIRequestFactory
)
from ..models import User
from ...authentication.views import (VerifyAccount,
                                     RegistrationAPIView
                                     )


class BaseTestArticles(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.data = {
            "user": {
                "email": "ar1@gmail.com",
                "username": "henry1",
                "password": "Password@1"
            }
        }
        self.login_credentials = {
            "user": {
                "email": "ar1@gmail.com",
                "password": "Password@1"
            }
        }

        self.article = {

            "article": {
                "title": "How to  train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
<<<<<<< HEAD
                "tagList": ["reactjs", "haskell", "ruby", "rails", "magic!"],
=======
>>>>>>> feat(articles) user can favorite article
                "image": {
                        "image_url": "http//url",
                        "image_description": "image is cool"
                }
            }
        }

<<<<<<< HEAD

        self.updated_article = {

            "article": {
                "title": "How to  train your dragon updated",
                "description": "Ever wonder how ggggg?",
                "body": "You have to believe",
                "tagList": ["reactjs", "angularjs", "dragons"],
                "image": {
                        "image_url": "http//url",
                        "image_description": "image is cooljjjj"
                }
            }
        }
        self.article_log_tile = {

            "article": {
                "title": "How to  train your dragon"*200,
                "description": "Ever wonder how?",
                "body": "You have to believe",
=======
        self.article_log_tile = {

            "article": {
                "title": "How to  train your dragon"*200,
                "description": "Ever wonder how?",
                "body": "You have to believe",
                "image": {
                        "image_url": "http//url",
                        "image_description": "image is cool"
                }
            }
        }

        self.article_big_body = {

            "article": {
                "title": "How to  train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe"*200,
>>>>>>> feat(articles) user can favorite article
                "image": {
                        "image_url": "http//url",
                        "image_description": "image is cool"
                }
            }
        }
<<<<<<< HEAD
=======

        self.updated_article = {

            "article": {
                "title": "How to  train your dragon updated",
                "description": "Ever wonder how ggggg?",
                "body": "You have to believe",
                "image": {
                        "image_url": "http//url",
                        "image_description": "image is cooljjjj"
                }
            }
        }
>>>>>>> feat(articles) user can favorite article
        url = reverse('registration')
        self.client.post(url, self.data, format='json')

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

    def login_user(self):

        request = APIRequestFactory().post(
            reverse("registration")
        )
        user = User.objects.get()
        token, uidb64 = RegistrationAPIView.generate_activation_link(
            user, request, send=False)
        self.verify_account(token, uidb64)
        response = self.client.post(
            '/api/users/login/', self.login_credentials, format='json')
        jwt_token = response.data['token']
        return jwt_token
