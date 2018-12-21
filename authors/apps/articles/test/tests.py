import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import APITestCase, APIClient
from .base import BaseTestArticles
from .test_create_articles import TestArticles

class TestRate(TestArticles, BaseTestArticles):

    def test_rate_article(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer '+ self.login_user()
        )
        response = self.client.post(
            '/api/articles/{}/rate/'.format(slug), data=self.rate,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_wrong_input_for_rating_article(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer '+ self.login_user()
        )
        response = self.client.post(
            '/api/articles/{}/rate/'.format(slug), data=self.rate_wrong,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_re_rate_article(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer '+ self.login_user()
        )
        response1 = self.client.post(
            '/api/articles/{}/rate/'.format(slug), data=self.rate,
            format='json'
        )
        response2 = self.client.post(
            '/api/articles/{}/rate/'.format(slug), data=self.re_rate,
            format='json'
        )
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)


