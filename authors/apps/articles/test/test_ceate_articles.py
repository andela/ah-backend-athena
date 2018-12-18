import json
from .base import BaseTestArticles
from rest_framework.views import status
from ..models import Article
from ...authentication.models import User
from ....apps.profiles.models import Profile


class TestArticles(BaseTestArticles):

    def data3_user_jwt(self):
        return User.objects.create_user(**self.data3['user']).token()

    def test_create_models_article(self):
        user = User.objects.create_user(
            username='henry', email='henry@gmail.com',
            password='Pass12')
        user.is_verified = True
        user = User.objects.filter(email='henry@gmail.com').first()
        author = Profile.objects.get(user_id=user.id)
        article = Article.objects.create(
            title='article title', author=author)
        self.assertEqual(str(article), article.title)

    def create_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        return response.data['slug']

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

    def test_get_article_tags(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/', data=self.article, format='json')
        slug = self.create_article()
        response = self.client.get(
            '/api/{}/tags/'.format(slug, format='json')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_tag(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/', data=self.article, format='json')
        slug = self.create_article()
        response = self.client.delete(
            '/api/{}/tags/magic!/'.format(slug, format='json')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_article_not_author(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        response = json.loads(response.content)
        slug = response['article']['slug']

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.data3_user_jwt())
        res = self.client.delete(
            '/api/articles/{}/'.format(slug))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            json.loads(res.content)['article']['error'],
            'You can only delete your own articles'
        )
