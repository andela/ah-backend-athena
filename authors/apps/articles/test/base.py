from django.test import TestCase

import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import (
    APITestCase,
    APIClient,
    APIRequestFactory
)
from ..apps import ArticlesConfig
from authors.apps.profiles.apps import ProfilesConfig
from ..models import User
from ...authentication.views import (VerifyAccount,
                                     RegistrationAPIView)


class BaseTestArticles(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.roni = self.save_user('roni', 'roni@a.com', 'P@ssword23lslsn')
        self.sama = self.save_user('sama', 'samantha@a.com', 'P@ssword23lslsn')

        self.data = {
            "user": {
                "email": "ar1@gmail.com",
                "username": "henry1",
                "password": "Password@1"
            }
        }

        self.data3 = {
            "user": {
                "email": "ak1@gmail.com",
                "username": "lhenry1",
                "password": "Password@1"
            }
        }
        self.login_credentials = {
            "user": {
                "email": "ar1@gmail.com",
                "password": "Password@1"
            }
        }

        self.rate = {
            "rating": 3
        }
        self.rate_wrong = {
            "rating": 9
        }
        self.re_rate = {
            "rating": 4
        }
        self.article = {

            "article": {
                "title": "How to  train your dragon added on the titlt",
                "description": "Ever wonder how?",
                "body": "You have to believe this body has beeb updated ",
                "tagList": ["Rails", "Golang", "magic!"],
                "images": [
                       {
                           "image_url": "https://imgur.comhenry/",
                           "description": "image is cool"
                       },
                    {
                           "image_url": "https://imgur.comhenry/",
                           "description": "image is cool"
                       },
                    {
                           "image_url": "https://imgur.comhenry/",
                           "description": "image is cool"
                       }
                ]
            }
        }
        self.article2 = {

            "article": {
                "title": "How to  train your dragon added on the titlt",
                "description": "Ever wonder how?",
                "body": "You have to believe this body has beeb updated "*100,
                "tagList": ["Rails", "Golang", "magic!"],
                "images": [
                       {
                           "image_url": "https://imgur.comhenry/",
                           "description": "image is cool"
                       },
                    {
                           "image_url": "https://imgur.comhenry/",
                           "description": "image is cool"
                       },
                    {
                           "image_url": "https://imgur.comhenry/",
                           "description": "image is cool"
                       }
                ]
            }
        }

        self.comment = {
            "comment": {
                "comment_body": "Hey, this is another comment for you "
            }
        }

        self.article_log_tile = {

            "article": {
                "title": "How to  train your dragon"*200,
                "description": "Ever wonder how?",
                "body": "You have to believe",
                "images": [{
                        "image_url": "http//url",
                        "description": "image is cool"
                }],
            }
        }

        self.article_big_body = {

            "article": {
                "title": "How to  train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe"*200,
                "images": [{
                        "image_url": "https://imgur.comdhenry/",
                        "description": "image is cool"
                }],
            }
        }

        self.report_article_data = {

            "report": {
                "reason": "article contains porn"
            }
        }

        self.report_article_data_empty_reason = {

            "report": {
                "reason": ""
            }
        }

        self.updated_article = {

            "article": {
                "title": "How to  train your dragon updated",
                "description": "Ever wonder how ggggg?",
                "body": "You have to believe",
                "images": [{
                        "id": 1,
                        "image_url": "https://imgur.comdhenry/",
                        "description": "image is cooljjjj"
                }],
            }
        }
        self.article_log_tile = {

            "article": {
                "title": "How to  train your dragon"*200,
                "description": "Ever wonder how?",
                "body": "You have to believe",
                "images": {
                        "image_url": "http//url",
                        "image_description": "image is cool"
                }
            }
        }
        url = reverse('registration')
        self.client.post(url, self.data, format='json')

    def test_article_app_runing(self):
        self.assertTrue(ArticlesConfig)
        self.assertEqual(ArticlesConfig.name, 'articles')

    def test_profile_app_running(self):
        self.assertTrue(ProfilesConfig)
        self.assertEqual(ProfilesConfig.name, 'profiles')

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

    def create_article_to_share(self):
        """
        create & return an article that will be used for sharing
        """
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.get_samantha_token()))
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        return response.data
