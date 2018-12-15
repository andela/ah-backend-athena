from django.test import TestCase

import json
from ..test.base import BaseTestArticles


class TestComment(BaseTestArticles):

    def test_comment_on_article_which_doesnot_exist(self):
        fake_slug = 'am_a_fake_slug'
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        res = self.client.post(
            '/api/articles/{}/comments/'.format(fake_slug),
            self.comment, format='json')
        self.assertTrue(res.status_code, 404)
        self.assertIn(
            'Sorry, this article does not exist',
            str(res.content))

    def test_comment_created_successfully(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        res = self.client.post(
            '/api/articles/{}/comments/'.format(self.create_article()),
            self.comment, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertIn("comment_body", str(res.content))

    def test_failed_to_update_comment(self):
        comment_id = 1000
        data = {
            "comment": {
    	    "article": "how-to-train-717b1570ca85",
			"comment_body": "Hey, this is another"	
            }
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        resp = self.client.put(
            '/api/articles/{}/comments/{}/'.format(self.create_article, comment_id),
            data, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn(
            'Failed to update, comment or article doesnot exist',
            str(resp.content))

    def test_comment_updated_successfully(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        data = {
            "comment": {
    	    "article": response.data['id'],
			"comment_body": "new update message"	
            }
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        res = self.client.post(
            '/api/articles/{}/comments/'.format(self.create_article()),
            self.comment, format='json')
        comment_id = res.data['id']
        resp = self.client.put(
            '/api/articles/{}/comments/{}/'.format(self.create_article(), comment_id),
            data, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(
            '"comment_body":"new update message"',
            str(resp.content))

    def test_users_only_update_their_comments(self):
        data = {
            "comment": {
			"comment_body": "new update message"	
            }
        }
        returned_slug_article = self.create_article()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_roni_token())
        res = self.client.post(
            '/api/articles/{}/comments/'.format(returned_slug_article),
            self.comment, format='json')
        comment_id = res.data['id']
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.get_samantha_token())
        resp = self.client.put(
            '/api/articles/{}/comments/{}/'.format(returned_slug_article, comment_id),
            data, format='json')
        self.assertEqual(resp.status_code, 403)
        self.assertIn(
            'You dont have permission to perform this action',
            str(resp.content))

    def test_user_cant_delete_another_users_comment(self):
        data = {
            "comment": {
			"comment_body": "new update message"	
            }
        }
        returned_slug_article = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.get_roni_token())
        res = self.client.post(
            '/api/articles/{}/comments/'.format(returned_slug_article),
            self.comment, format='json')
        comment_id = res.data['id']
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.get_samantha_token())
        resp = self.client.delete(
            '/api/articles/{}/comments/{}/'
            .format(returned_slug_article, comment_id),
            data, format='json')
        self.assertEqual(resp.status_code, 403)
        self.assertIn(
            'You dont have permission to perform this action',
            str(resp.content))

    def test_user_try_to_delete_a_comment_which_doesnt_exist(self):
        comment_id = 10000
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.get_samantha_token())
        resp = self.client.delete(
            '/api/articles/{}/comments/{}/'
            .format(self.create_article(), comment_id),
            format='json')
        self.assertEqual(resp.status_code, 404)
        self.assertIn(
            "Failed, comment or article does not exist",
            str(resp.content))

    def test_user_can_successfully_delete_comment_from_article(self):
        data = {
            "comment": {
			"comment_body": "new update message"	
            }
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_roni_token())
        res = self.client.post(
            '/api/articles/{}/comments/'.format(self.create_article()),
            self.comment, format='json')
        comment_id = res.data['id']
        resp = self.client.delete(
            '/api/articles/{}/comments/{}/'
            .format(self.create_article(), comment_id),
            data, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(
            'Comment deleted successfully',
            str(resp.content))

    def test_user_successfully_reply_to_a_comment(self):
        data = {
            "reply": {
	            "comment_body": "This is the reply body"
                }
	        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        res = self.client.post(
            '/api/articles/{}/comments/'.format(self.create_article()),
            self.comment, format='json')
        comment_id = res.data['id']
        resp = self.client.post(
            '/api/articles/{}/comments/{}/'
            .format(self.create_article(), comment_id),
            data, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertIn("comment_body", str(resp.content))

    def test_user_try_to_reply_on_a_comment_which_doesnt_exist(self):
        data = {
            "reply": {
	            "comment_body": "This is the reply body"
                }
	        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/{}/comments/'.format(self.create_article()),
            self.comment, format='json')
        comment_id = 100000000
        resp = self.client.post(
            '/api/articles/{}/comments/{}/'
            .format(self.create_article(), comment_id),
            data, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn("object does not exist.", str(resp.content))

    def test_get_all_comments_of_article(self):
        returned_slug_article = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/{}/comments/'.format(returned_slug_article),
            self.comment, format='json')
        res = self.client.get(
            '/api/articles/{}/comments/'.format(returned_slug_article),
            self.comment, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(1, len(res.data['comments']))

    def test_try_to_get_comments_with_invalid_slug(self):
        returned_slug_article = 'Fake slug'
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/{}/comments/'.format(returned_slug_article),
            self.comment, format='json')
        res = self.client.get(
            '/api/articles/{}/comments/'.format(returned_slug_article),
            self.comment, format='json')
        self.assertEqual(res.status_code, 404)
        self.assertTrue("Failed, comment or article doesnot exist", res.data)

    def test_get_all_replies_on_the_comment(self):
        returned_slug_article = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        resp = self.client.post(
            '/api/articles/{}/comments/'.format(returned_slug_article),
            self.comment, format='json')
        comment_id = resp.data['id']
        res = self.client.get(
            '/api/articles/{}/comments/{}/'
            .format(returned_slug_article, comment_id),
            self.comment, format='json')
        self.assertEqual(res.status_code, 200)

        

