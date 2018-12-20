"""
This module contains the test suite for unit
tests related to testing the sharing an article
functionality
"""
import json
from unittest.mock import patch
from rest_framework.views import status
from twitter import Status
from twitter.error import TwitterError
from .base import BaseTestArticles
from ...authentication.social.twitter_token_validator import TwitterValidate
from ..share import ShareArticle
from ..exceptions import FailedToSendEmailException, TwitterExceptionRaised


class TestArticleSharing(BaseTestArticles):
    """
    This class holds all our unit tests for article sharing
    """

    def return_article_slug(self):
        """
        This method returns an article slug. Used a placeholder method
        so there's no confusion as to what is being returned
        """
        return self.create_article_to_share()['slug']

    def test_facebook_share_correctly(self):
        """
        This test sharing an article with a valid token returns a 201-CREATED and a success message
        """
        article_slug = self.return_article_slug()
        res = self.client.post(
            '/api/articles/{}/share/facebook/'.format(article_slug))
        self.assertEqual(res.status_code, status.HTTP_201_CREATED,
                         "Response status should be 201 CREATED")
        self.assertIn("facebook_link", json.loads(res.content)['article'])

    def test_valid_twitter_tokens(self):
        """
        testcase verifies that user tokens when valid return data
        """
        article_slug = self.return_article_slug()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.get_samantha_token())

        with patch('authors.apps.articles.share' +
                   '.ShareArticle.share_via_twitter')as mock_twitter_share:
            with patch('authors.apps.articles.share' +
                       '.TwitterValidate.validate_twitter_token')as mock_twitter_validate:
                mock_twitter_share.return_value = "status text that was shared"
                mock_twitter_validate.return_value = {
                    "name": "andrew",
                    "email": "andrew@a.com",
                    "id_str": "104383024388008549815"
                }
                res = self.client.post(
                    '/api/articles/{}/share/twitter/'.format(article_slug),
                    {'tokens': 'valid_token_key valid_token_secret'}, format='json')

                self.assertEqual(res.status_code, status.HTTP_201_CREATED,
                                 "Response status code should be a 201_CREATED")
                self.assertEqual(json.loads(res.content).get('article').get(
                    'success'), "Article link shared to twitter")

    def test_twitter_validate_token_is_called(self):
        """
        tests that we actually call the TwitterValidate.validate_twitter_token method
        """
        article_slug = self.return_article_slug()
        with patch('authors.apps.articles.share' +
                   '.TwitterValidate.validate_twitter_token') as mock_twitter_validate:
            mock_twitter_validate.return_value = {
                "name": "andrew",
                "email": "andrew@a.com",
                "id_str": "104383024388008549815"
            }
            with patch('authors.apps.articles.share' +
                       '.TwitterValidate.extract_tokens') as mock_extract_twitter_tokens:
                with patch('authors.apps.articles.share' +
                           '.twitter.Api.PostUpdate') as mock_post_to_twitter:
                    mock_extract_twitter_tokens.return_value = (
                        'tokens', 'tokens')
                    mock_post_to_twitter.return_value = Status(
                        text="status updated with a link to the article")
                    ShareArticle.share_via_twitter('tokens tokens', 'url')
                    self.assertTrue(mock_twitter_validate.called)
                    self.assertTrue(mock_post_to_twitter.called)
                    self.assertEqual(
                        len(mock_extract_twitter_tokens('token_key', 'token_secret')), 2)
                    self.assertEqual(ShareArticle.share_via_twitter(
                        'tokens tokens', 'url'), "status updated with a link to the article")
                    mock_post_to_twitter.side_effect = TwitterError(
                        {'message': 'some twitter error occured'})
                    with self.assertRaises(TwitterExceptionRaised):
                        ShareArticle.share_via_twitter('tokens tokens', 'url')

    def test_verify_twitter_auth_raises_exception_when_token_is_invalid(self):
        """
        tests if exception is raised when we receive invalid tokens
        """
        article_slug = self.return_article_slug()
        with patch('authors.apps.articles.share' +
                   '.TwitterValidate.validate_twitter_token') as mock_twitter_validate:
            mock_twitter_validate.return_value = None
            res = self.client.post(
                '/api/articles/{}/share/twitter/'.format(article_slug),
                {'tokens': 'valid_token_key valid_token_secret'}, format='json')
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(json.loads(res.content), {'article': {
                'detail': 'The access_token provided is invalid'}})

    def test_missing_access_tokens(self):
        """
        testcase checks for validation error raised when
        twitter access tokens are not provided
        """
        article_slug = self.return_article_slug()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.get_samantha_token())
        res = self.client.post(
            '/api/articles/{}/share/twitter/'.format(article_slug))
        res_email = self.client.post(
            '/api/articles/{}/share/email/'.format(article_slug))

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST,
                         "Response status code should be a 400_BAD_REQUEST")
        self.assertEqual(json.loads(res.content), {"article": {
            "detail": "Missing tokens parameter in the request body, it is required"}})
        self.assertEqual(res_email.status_code, status.HTTP_400_BAD_REQUEST,
                         "Response status code should be a 400_BAD_REQUEST")
        self.assertEqual(json.loads(res_email.content), {"article": {
            "detail": "Missing 'send_to' (Email address to share to)" +
            " parameter in the request body, it is required"}})

    def test_article_does_not_exist(self):
        """
        testcase checks for validation error raised when
        supplied slug does not match any saved articles
        """
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.get_samantha_token())
        res = self.client.post(
            '/api/articles/{}/share/twitter/'.format("random_non_existent_slug"))
        res_email = self.client.post(
            '/api/articles/{}/share/email/'.format("random_non_existent_slug"),
            {'email': 'andrew@a.com'}, format='json')
        res_facebook = self.client.post(
            '/api/articles/{}/share/facebook/'.format("random_non_existent_slug"))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND,
                         "Response status code should be a 404_NOT_FOUND")
        self.assertEqual(json.loads(res.content), {"article": {
            "detail": "This article does not exist."}})
        self.assertEqual(res_email.status_code, status.HTTP_404_NOT_FOUND,
                         "Response status code should be a 404_NOT_FOUND")
        self.assertEqual(json.loads(res_email.content), {"article": {
            "detail": "This article does not exist."}})
        self.assertEqual(res_facebook.status_code, status.HTTP_404_NOT_FOUND,
                         "Response status code should be a 404_NOT_FOUND")
        self.assertEqual(json.loads(res_facebook.content), {"article": {
            "detail": "This article does not exist."}})

    def test_tokens_not_separated_by_a_space(self):
        """
        testcase checks for validation error raised when
        supplied tokens are not separated by a space
        """
        article_slug = self.return_article_slug()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.get_samantha_token())
        res = self.client.post(
            '/api/articles/{}/share/twitter/'.format(article_slug),
            {'tokens': 'token1-token2'}, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST,
                         "Response status code should be a 400_BAD_REQUEST")
        self.assertEqual(json.loads(res.content), {"article": {
            "detail": "Invalid format supplied twitter credentials. " +
            "Correct format is: '<access_token_key> <access_token_secret>'"}})

    def test_invalid_email_syntax(self):
        """
        testcase checks for validation error raised when
        supplied email is invalid (syntactically)
        """
        article_slug = self.return_article_slug()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.get_samantha_token())
        res = self.client.post(
            '/api/articles/{}/share/email/'.format(article_slug),
            {'send_to': 'email-email'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST,
                         "Response status code should be a 400_BAD_REQUEST")
        self.assertEqual(json.loads(res.content), {"article": {
            "detail": "The email string provided is invalid"}})

    def test_valid_email_share(self):
        """
        this test method checks that when all the data supplied is valid and there are no errors,
        the applicaiton responds correctly.
        """
        article_slug = self.return_article_slug()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.get_samantha_token())
        res = self.client.post(
            '/api/articles/{}/share/email/'.format(article_slug),
            {'send_to': 'andrew@a.com'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(res.content).get('article').get('success'),
                         "Article link sent to andrew@a.com")

    def test_send_mail_error_occurs(self):
        """
        This test method checks that when an error occurs during
        the send_mail call, the error is handled properly.
        """
        with patch('authors.apps.articles.views' +
                   '.send_mail') as mock_send_mail:
            mock_send_mail.side_effect = FailedToSendEmailException
            with self.assertRaises(FailedToSendEmailException):
                mock_send_mail(subject='subject', message='message', from_email='email_from',
                               recipient_list='recipient_list', fail_silently=False)
