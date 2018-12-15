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

        self.roni = self.save_user('roni', 'roni@a.com', 'P@ssword23lslsn')
        self.sama = self.save_user('sama', 'samantha@a.com', 'P@ssword23lslsn')

        self.data = {
            "user": {
                "email": "kasule06joseph@gmail.com",
                "username": "henry1",
                "password": "kasule89990"
            }
        }
        self.data2 = {
            "user": {
                "email": "joseph.kasule@andela.com",
                "username": "henry1",
                "password": "kasule89990"
            }
        }
        self.login_credentials = {
            "user": {
                "email": "kasule06joseph@gmail.com",
                "password": "kasule89990"
            }
        }
        self.new_user = {
            "user": {
                "email": "joseph.kasule@andela.com",
                "password": "kasule89990"
            }
        }
        self.article = {

            "article": {
                "title": "How to  train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
                "image": {
                        "image_url": "http//url",
                        "image_description": "image is cool"
                }
            }
        }

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
                "image": {
                        "image_url": "http//url",
                        "image_description": "image is cool"
                }
            }
        }

        self. comment = {
            "comment": {
            "comment_body": "Hey, this is another comment for you "	
            }
        }

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
        url = reverse('registration')
        self.client.post(url, self.data, format='json')

    def save_user(self, username, email, pwd):
        validated_data = {'username': username,
                          'email': email, 'password': pwd}
        return User.objects.create_user(**validated_data)

    
    def get_samantha_token(self):
        return self.sama.token()

    def get_roni_token(self):
        return self.roni.token()

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
        return User.objects.filter().first().token()

    def create_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        return response.data['slug']
