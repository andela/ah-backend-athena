from django.test import TestCase

import json
from ..test.base import BaseTestArticles
 
class TestStats(BaseTestArticles):
    def test_read_statistics_updated_successfully(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        res = self.client.post(
            '/api/articles/{}/3'.format(self.create_article()),
            format='json')
        self.assertTrue(res.status_code, 200)
        self.assertEqual(1, res.data['read_count'])

    def test_user_count_for_a_read_is_only_one(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        res = self.client.post(
            '/api/articles/', data=self.article, format='json')
        slug = res.data['slug']
        self.client.post(
            '/api/articles/{}/3'.format(slug),
            format='json')
        resp = self.client.post(
            '/api/articles/{}/3'.format(slug),
            format='json')
        self.assertTrue(resp.status_code, 200)
        self.assertEqual(1, resp.data['read_count'])

    def test_a_read_cannot_be_recorded_when_user_hasnot_read_the_article(self):
        data =  {

            "article": {
                "title": "How to  train your dragon added on the titlt",
                "description": "Ever wonder how?",
                "body": "You have to believe this body has beeb updated " * 100,
                "tagList": ["Rails", "Golang", "magic!"],
                "images": [
                       {
                           "image_url": "https://imgur.comhenry/",
                           "description": "image is cool"
                       }
                ]
            }
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        resp = self.client.post(
            '/api/articles/', data=data, format='json')
        slug = resp.data['slug']
        res = self.client.post(
            '/api/articles/{}/2'.format(slug),
            format='json')
        self.assertTrue(res.status_code, 301)
        self.assertEqual('read not recorded', res.data['message'])
        