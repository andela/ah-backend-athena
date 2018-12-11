import json
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from .base import BaseTestArticles


class TestFavouriteArticle(BaseTestArticles):

    def create_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        return response.data['slug']

    def test_favourite_article(self):
        """
        test for user favouriting article
        """
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/'+slug+'/favorite/',
            data=self.article,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "favourited",
            str(json.loads(response.content))
        )
    
        """
        tests article favourating conflict
        """
        response = self.client.post(
            '/api/articles/'+slug+'/favorite/',
            data=self.article,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn(
            "article already favorited",
            str(json.loads(response.content))
        )

    def test_unfavourite_article(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.delete(
            '/api/articles/'+slug+'/favorite/',
            data=self.article,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "article has been unfavorited",
            str(json.loads(response.content))
        )


    def test_favourite_wrong_article(self):
        """
        test for use favouriting wrong article
        """
        slug = 'chvgbjhnkjmjnhgfcvgbjhnkjlmk'
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/'+slug+'/favorite/',
            data=self.article,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "article doesnot exist",
            str(json.loads(response.content))
        )

    def test_unfavourite_wrong_article(self):
        """
        test for use favouriting wrong article
        """
        slug = 'chvgbjhnkjmjnhgfcvgbjhnkjlmk'
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.delete(
            '/api/articles/'+slug+'/favorite/',
            data=self.article,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "article doesnot exist",
            str(json.loads(response.content))
        )
