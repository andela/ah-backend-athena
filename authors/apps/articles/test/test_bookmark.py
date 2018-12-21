import json
from .base import BaseTestArticles
from rest_framework.views import status
from ..models import Article
from ...authentication.models import User
from ....apps.profiles.models import Profile


class TestBookmark(BaseTestArticles):

    def test_bookmark_successful(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        slug = response.data['slug']
        res = self.client.post(
            '/api/articles/{}/bookmark/'.format(slug),
            format='json'
        )
        self.assertEqual(res.status_code, 201)
        self.assertGreater(len(res.data), 1)

    def test_article_was_already_bookmarked(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        slug = response.data['slug']
        self.client.post(
            '/api/articles/{}/bookmark/'.format(slug),
            format='json'
        )
        res = self.client.post(
            '/api/articles/{}/bookmark/'.format(slug),
            format='json'
        )
        self.assertEqual(res.status_code, 301)
        self.assertEqual('article was bookmarked', res.data['message'])

    def test_article_does_not_exist(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/', data=self.article, format='json')
        slug = 'Fake slug'
        res = self.client.post(
            '/api/articles/{}/bookmark/'.format(slug),
            format='json'
        )
        self.assertEqual(res.status_code, 404)
        self.assertEqual("Article does not exist", res.data['error'])

    def test_all_get_bookmarked_articles(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        slug = response.data['slug']
        self.client.post(
            '/api/articles/{}/bookmark/'.format(slug),
            format='json'
        )
        res = self.client.get(
            '/api/article/bookmarks/',
            format='json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data['bookmark'])

    def test_bookmark_does_not_exist(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/', data=self.article, format='json')
        res = self.client.get(
            '/api/article/bookmarks/',
            format='json'
        )
        self.assertEqual(res.status_code, 404)
        self.assertEqual('Bookmarks not found', res.data['message'])

    def test_unbookmark_an_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.get_roni_token())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        slug = response.data['slug']
        resp = self.client.post(
            '/api/articles/{}/bookmark/'.format(slug),
            format='json'
        )
        id = resp.data['id']
        res = self.client.delete(
            '/api/articles/bookmark/{}/'.format(id),
            format='json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual("Article unbookmarked", res.data['message'])

    def test_delete_bookmark_does_not_exist(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.get_roni_token())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        slug = response.data['slug']
        resp = self.client.post(
            '/api/articles/{}/bookmark/'.format(slug),
            format='json'
        )
        id = 100
        res = self.client.delete(
            '/api/articles/bookmark/{}/'.format(id),
            format='json'
        )
        self.assertEqual(res.status_code, 404)
        self.assertEqual("bookmark does not exist", res.data['error'])

    def test_user_only_unbookmark_their_bookmarked_articles(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.get_roni_token())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        slug = response.data['slug']
        resp = self.client.post(
            '/api/articles/{}/bookmark/'.format(slug),
            format='json'
        )
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.get_samantha_token())
        id = resp.data['id']
        res = self.client.delete(
            '/api/articles/bookmark/{}/'.format(id),
            format='json'
        )
        self.assertEqual(res.status_code, 403)
        self.assertEqual("sorry, permission denied", res.data['message'])


        




