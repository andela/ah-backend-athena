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
        self.assertEqual("done", res.data['result'])