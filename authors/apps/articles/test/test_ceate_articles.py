from .base import BaseTestArticles
from rest_framework.views import status
from ..models import Article
import json


class TestArticles(BaseTestArticles):


    def test_create_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_article_long_title(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article_log_tile, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_article(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.get(
            '/api/articles/'+slug+'/',  format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_article_doesnot_exist(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        fake_slug = "ed"*23
        response = self.client.get(
            '/api/articles/{}/'.format(fake_slug),  format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_article(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.delete(
            '/api/articles/'+slug+'/',  format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_article_doesnot_exist(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        fake_slug = "ed"*23
        response = self.client.delete(
            '/api/articles/{}/'.format(fake_slug),  format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_existing_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        fake_slug = "ed"*23
        response = self.client.put(
            '/api/articles/ffhfh-ggrg/', data=self.updated_article, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_article(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.put(
            '/api/articles/'+slug+'/', data=self.updated_article, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_all_articles(self):
        self.create_article()
        self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.get(
            '/api/articles',  format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
