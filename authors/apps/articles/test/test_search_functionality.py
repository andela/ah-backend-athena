from rest_framework.views import status
from .base import BaseTestArticles
from ...authentication.models import User
from ....apps.profiles.models import Profile
from ..models import Article



class SearchFunctionalityTestCase(BaseTestArticles):

    def test_search_by_author(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/', data=self.article, format='json')
        self.client.post(
            '/api/articles/', data=self.article, format='json')
        response = self.client.get(
            '/api/articles/search?author=henry1',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_by_tag(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/', data=self.article, format='json')
        self.client.post(
            '/api/articles/', data=self.article, format='json')
        response = self.client.get(
            '/api/articles/search?tag=Rails',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_by_tag_and_author(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/', data=self.article, format='json')
        self.client.post(
            '/api/articles/', data=self.article, format='json')
        response = self.client.get(
            '/api/articles/search?tag=Rails&author=henry1',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

