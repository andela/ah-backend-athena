import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from ..views import VerifyAccount, RegistrationAPIView
from ..models import UserManager, User

from unittest.mock import patch, Mock, call
from ..social.google_token_validator import GoogleValidate
from ..social.facebook_token_validator import FacebookValidate
from ..social.twitter_token_validator import TwitterValidate
from ..views import GoogleAuthAPIView, FacebookAuthAPIView, TwitterAuthAPIView
from ..serializers import GoogleAuthSerializer

from google.auth.transport import requests


class TestUsers(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def generate_user(self, username='', email='', password=''):
        user = {
            'user': {
                'email': email,
                'username': username,
                'password': password
            }
        }
        return user

    def verify_account(self, token, uidb64):
        request = APIRequestFactory().get(
            reverse(
                "activate_account",
                kwargs={
                    "token": token,
                    "uidb64": uidb64}))
        verify_account = VerifyAccount.as_view()
        response = verify_account(request, token=token, uidb64=uidb64)
        return response

    def create_user(self, username='', email='', password=''):
        user = self.generate_user(username, email, password)
        self.client.post('/api/users/', user, format='json')
        return user

    def test_user_registration(self):
        user = self.generate_user(
            'athena', 'athena@gmail.com', 'password@user')
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            json.loads(
                response.content), {
                "user": {
                    "message": "A verification email has been sent to athena@gmail.com"}})
    
    def test_cannot_login_without_verification(self):
        self.create_user('athena', 'athena@gmail.com', 'password@user')
        login_details = self.generate_user(
            '', 'athena@gmail.com', 'password@user')
        response = self.client.post(
            '/api/users/login/', login_details, format='json')
        self.assertEqual(
            json.loads(
                response.content), {
                "errors": {
                    "error": ["Your email is not verified, Please check your email for a verification link"]}})
    
    def test_user_registration_empty_details(self):
        user = self.generate_user('', '', '')
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_wrong_email_format(self):
        user = self.generate_user('athena', 'athenmail', 'password@user')
        response = self.client.post('/api/users/', user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        self.create_user('athena', 'athena@gmail.com', 'password@user')
        login_details = self.generate_user(
            '', 'athena@gmail.com', 'password@user')
        request = APIRequestFactory().post(
            reverse("registration")
        )
        user = User.objects.get()
        token, uidb64 = RegistrationAPIView.generate_activation_link(
            user, request, send=False)
        self.verify_account(token, uidb64)
        response = self.client.post(
            '/api/users/login/', login_details, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            json.loads(response.content),
            {"user": {
                "email": "athena@gmail.com",
                "username": "athena",
                'token': response.data['token']
            }
            }
        )

    def test_unauthorized_access_to_authenticated_endpoint(self):
        self.create_user('kasule', 'athena@gmail.com', 'Password@user1')
        login_details = self.generate_user(
            '', 'athena@gmail.com', 'Password@user1')
        response = self.client.post(
            '/api/user/', login_details, format='json')
        self.assertTrue(response.status_code == 403)
        self.assertEqual(
            json.loads(response.content),
            {"user": {
                "detail": "Authentication credentials were not provided."
            }
            }
        )

    def test_user_with_valid_token_access_protected_endpoints(self):
        self.create_user('soko', 'athena@gmail.com', 'Password@user1')
        login_details = self.generate_user(
            '', 'athena@gmail.com', 'Password@user1')
        request = APIRequestFactory().post(
            reverse("registration")
        )
        user = User.objects.get()
        token, uidb64 = RegistrationAPIView.generate_activation_link(
            user, request, send=False)
        self.verify_account(token, uidb64)
        response = self.client.post(
            '/api/users/login/', login_details, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        res = self.client.get(
            '/api/user/', login_details, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            json.loads(res.content),
            {"user": {
                "email": "athena@gmail.com",
                "username": "soko",
                'token': res.data['token']
            }
            }
        )

    def test_invalid_token(self):
        self.create_user('josh', 'athena@gmail.com', 'Password@user1')
        login_details = self.generate_user(
            '', 'athena@gmail.com', 'Password@user1')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + '123hjhj12')
        res = self.client.get(
            '/api/user/', login_details, format='json')
        self.assertTrue(res.status_code == 401)
        self.assertEqual(
            'Invalid token. please login again', res.data['detail'])

    def test_login_jwt_with_bad_credentials(self):
        self.create_user('kica', 'athena@gmail.com', 'Password@user11')
        login_details = self.generate_user(
            '', 'kica@gmail.com', 'Password@user11')
        response = self.client.post(
            '/api/users/login/', login_details, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"errors": {
                "error": [
                    "A user with this email and password was not found."]
            }
            },
            json.loads(response.content))


class TestSocialAuthUsers(APITestCase):

    def save_user_to_db(self, username='', email='', password=''):
        user = {
            'user': {
                'email': email,
                'username': username,
                'password': password
            }
        }
        self.client.post('/api/users/', user, format='json')

    def test_google_validate_token_is_called(self):
        with patch('authors.apps.authentication.social.google_token_validator.id_token.verify_oauth2_token') as mock_google_validate:
            GoogleValidate.validate_google_token('access token')
            self.assertTrue(mock_google_validate.called)

    def test_verify_google_auth_raises_exception_when_token_is_invalid(self):
        with patch('authors.apps.authentication.social.google_token_validator.id_token.verify_oauth2_token') as mock_google_validate:
            GoogleValidate.validate_google_token('token')
            mock_google_validate.side_effect = ValueError
            self.assertRaises(ValueError, mock_google_validate)
            self.assertIsNone(GoogleValidate.validate_google_token('token'))

    def test_google_validate_returns_correct_data_when_token_is_valid(self):
        google_user_info_valid_response = {
            "name": "andrew", "email": "andrew@a.com", "sub": "104383024388008549815"}
        with patch('authors.apps.authentication.social.google_token_validator.GoogleValidate.validate_google_token') as mock_google_validate:
            mock_google_validate.return_value = google_user_info_valid_response
            self.assertEqual(mock_google_validate(
                'VALID google token'), google_user_info_valid_response)

    def test_google_validate_returns_none_when_token_is_invalid(self):
        with patch('authors.apps.authentication.social.google_token_validator.GoogleValidate.validate_google_token') as mock_google_validate:
            mock_google_validate.return_value = None
            self.assertIsNone(mock_google_validate('INVALID google token'))

    def test_google_login_valid_token(self):
        with patch('authors.apps.authentication.social.google_token_validator.GoogleValidate.validate_google_token') as mock_google_validate:
            mock_google_validate.return_value = {
                "name": "andrew", "email": "andrew@a.com", "sub": "104383024388008549815"}
            res = self.client.post(
                '/api/users/google/', {"token": "valid token for google"}, format='json')
            self.assertEqual(res.status_code, status.HTTP_200_OK,
                             "Response status should be 200 OK")
            self.assertIn("jwt_token", json.loads(res.content)['user'])


    def test_google_login_invalid_token(self):
        with patch('authors.apps.authentication.social.google_token_validator.GoogleValidate.validate_google_token') as mock_google_validate:
            mock_google_validate.return_value = None
            res = self.client.post(
                '/api/users/google/', {"token": "valid token for google"}, format='json')
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST,
                             "Response status should be 400 BAD REQUEST")
            self.assertEqual(json.loads(res.content), {"errors": {
                             "auth_token": ["Invalid token please try again"]}})

    def test_google_login_missing_key_sub_should_return_error(self):
        with patch('authors.apps.authentication.social.google_token_validator.GoogleValidate.validate_google_token') as mock_google_validate:
            mock_google_validate.return_value = {
                "name": "andrew", "email": "andrew@a.com", "some_other_thing": "104383024388008549815"}
            res = self.client.post(
                '/api/users/google/', {"token": "valid token for google"}, format='json')
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST,
                             "Response status should be 400 BAD REQUEST")
            self.assertEqual(json.loads(res.content), {"errors": {
                             "auth_token": ["Token is not valid or has expired. Please get a new one."]}})

    def test_google_user_with_attached_email_already_exists_in_db(self):
        self.save_user_to_db('andrew','andrew@a.com','P@ssword')
        with patch('authors.apps.authentication.social.google_token_validator.GoogleValidate.validate_google_token') as mock_google_validate:
            mock_google_validate.return_value = {
                "name": "andrew", "email": "andrew@a.com", "sub": "104383024388008549815"}
            res = self.client.post(
                '/api/users/google/', {"token": "valid token for google"}, format='json')
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST,
                                "Response status should be 400 BAD REQUEST")
            self.assertEqual(json.loads(res.content), {"errors": {
                             "auth_token": ["Failed to register the user. Email already exists in the database"]}})

    def test_facebook_validate_token_is_called(self):
        with patch('authors.apps.authentication.social.facebook_token_validator.facebook.GraphAPI') as mock_facebook_validate:
            FacebookValidate.validate_facebook_token('access token')
            self.assertTrue(mock_facebook_validate.called)
            mock_facebook_validate.assert_called_with(
                access_token='access token', version='3.1')

    def test_verify_facebook_auth_raises_exception_when_token_is_invalid(self):
        with patch('authors.apps.authentication.social.facebook_token_validator.facebook.GraphAPI') as mock_facebook_validate:
            FacebookValidate.validate_facebook_token('token')
            mock_facebook_validate.side_effect = ValueError
            self.assertRaises(ValueError, mock_facebook_validate)
            self.assertIsNone(
                FacebookValidate.validate_facebook_token('token'))

    def test_facebook_validate_returns_correct_data_when_token_is_valid(self):
        facebook_user_info_valid_response = {
            "name": "andrew", "email": "andrew@a.com", "id": "104383024388008549815"}
        with patch('authors.apps.authentication.social.facebook_token_validator.FacebookValidate.validate_facebook_token') as mock_facebook_validate:
            mock_facebook_validate.return_value = facebook_user_info_valid_response
            self.assertEqual(mock_facebook_validate(
                'VALID facebook token'), facebook_user_info_valid_response)

    def test_facebook_validate_returns_none_when_token_is_invalid(self):
        with patch('authors.apps.authentication.social.facebook_token_validator.FacebookValidate.validate_facebook_token') as mock_facebook_validate:
            mock_facebook_validate.return_value = None
            self.assertIsNone(mock_facebook_validate('INVALID facebook token'))

    def test_facebook_login_valid_token(self):
        with patch('authors.apps.authentication.social.facebook_token_validator.FacebookValidate.validate_facebook_token') as mock_facebook_validate:
            mock_facebook_validate.return_value = {
                "name": "andrew", "email": "andrew@a.com", "id": "104383024388008549815"}
            mock_facebook_validate('token')
            res = self.client.post(
                '/api/users/facebook/', {"token": "valid token for facebook"}, format='json')
            self.assertEqual(res.status_code, status.HTTP_200_OK,
                             "Response status should be 200 OK")
            self.assertIn("jwt_token", json.loads(res.content)['user'])

    def test_facebook_login_invalid_token(self):
        with patch('authors.apps.authentication.social.facebook_token_validator.FacebookValidate.validate_facebook_token') as mock_facebook_validate:
            mock_facebook_validate.return_value = None
            res = self.client.post(
                '/api/users/facebook/', {"token": "invalid token for facebook"}, format='json')
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST,
                             "Response status should be 400 BAD REQUEST")
            self.assertEqual(json.loads(res.content), {"errors": {
                             "auth_token": ["Invalid token please try again"]}})

    def test_facebook_login_missing_key_sub_should_return_error(self):
        with patch('authors.apps.authentication.social.facebook_token_validator.FacebookValidate.validate_facebook_token') as mock_facebook_validate:
            mock_facebook_validate.return_value = {
                "name": "andrew", "email": "andrew@a.com", "some_other_thing": "104383024388008549815"}
            res = self.client.post(
                '/api/users/facebook/', {"token": "valid token for facebook"}, format='json')
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST,
                             "Response status should be 400 BAD REQUEST")
            self.assertEqual(json.loads(res.content), {"errors": {
                             "auth_token": ["Token is not valid or has expired. Please get a new one."]}})

    def test_facebook_user_with_attached_email_already_exists_in_db(self):
        self.save_user_to_db('andrew','andrew@a.com','P@ssword')
        with patch('authors.apps.authentication.social.facebook_token_validator.FacebookValidate.validate_facebook_token') as mock_facebook_validate:
            mock_facebook_validate.return_value = {
                "name": "andrew", "email": "andrew@a.com", "id": "104383024388008549815"}
            res = self.client.post(
                '/api/users/facebook/', {"token": "valid token for facebook"}, format='json')
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST,
                                "Response status should be 400 BAD REQUEST")
            self.assertEqual(json.loads(res.content), {"errors": {
                             "auth_token": ["Failed to register the user. Email already exists in the database"]}})

    def test_twitter_validate_token_is_called(self):
        with patch('authors.apps.authentication.social.twitter_token_validator.twitter.Api') as mock_twitter_validate:
            TwitterValidate.validate_twitter_token('access token')
            self.assertTrue(mock_twitter_validate.called)

    def test_verify_twitter_auth_raises_exception_when_token_is_invalid(self):
        with patch('authors.apps.authentication.social.twitter_token_validator.twitter.Api') as mock_twitter_validate:
            TwitterValidate.validate_twitter_token('token1 token2')
            mock_twitter_validate.side_effect = ValueError
            self.assertRaises(ValueError, mock_twitter_validate)
            self.assertIsNone(TwitterValidate.validate_twitter_token('token'))

    def test_twitter_validate_returns_correct_data_when_token_is_valid(self):
        twitter_user_info_valid_response = {
            "name": "andrew", "email": "andrew@a.com", "id_str": "104383024388008549815"}
        with patch('authors.apps.authentication.social.twitter_token_validator.TwitterValidate.validate_twitter_token') as mock_twitter_validate:
            mock_twitter_validate.return_value = twitter_user_info_valid_response
            self.assertEqual(mock_twitter_validate(
                'VALID twitter token'), twitter_user_info_valid_response)

    def test_twitter_validate_returns_none_when_token_is_invalid(self):
        with patch('authors.apps.authentication.social.twitter_token_validator.TwitterValidate.validate_twitter_token') as mock_twitter_validate:
            mock_twitter_validate.return_value = None
            self.assertIsNone(mock_twitter_validate('INVALID twitter token'))

    def test_twitter_login_valid_token(self):
        with patch('authors.apps.authentication.social.twitter_token_validator.TwitterValidate.validate_twitter_token') as mock_twitter_validate:
            mock_twitter_validate.return_value = {
                "name": "andrew", "email": "andrew@a.com", "id_str": "104383024388008549815"}
            mock_twitter_validate('token')
            res = self.client.post(
                '/api/users/twitter/', {"token": "valid token for twitter"}, format='json')
            self.assertEqual(res.status_code, status.HTTP_200_OK,
                             "Response status should be 200 OK")
            self.assertIn("jwt_token", json.loads(res.content)['user'])

    def test_twitter_login_invalid_token(self):
        with patch('authors.apps.authentication.social.twitter_token_validator.TwitterValidate.validate_twitter_token') as mock_twitter_validate:
            mock_twitter_validate.return_value = None
            res = self.client.post(
                '/api/users/twitter/', {"token": "valid token for twitter"}, format='json')
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST,
                             "Response status should be 400 BAD REQUEST")
            self.assertEqual(json.loads(res.content), {"errors": {
                             "auth_token": ["Invalid token please try again"]}})

    def test_twitter_login_missing_key_sub_should_return_error(self):
        with patch('authors.apps.authentication.social.twitter_token_validator.TwitterValidate.validate_twitter_token') as mock_twitter_validate:
            mock_twitter_validate.return_value = {
                "name": "andrew", "email": "andrew@a.com", "some_other_thing": "104383024388008549815"}
            res = self.client.post(
                '/api/users/twitter/', {"token": "valid token for twitter"}, format='json')
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST,
                             "Response status should be 400 BAD REQUEST")
            self.assertEqual(json.loads(res.content), {"errors": {
                             "auth_token": ["Token is not valid or has expired. Please get a new one."]}})
    
    def test_twitter_user_with_attached_email_already_exists_in_db(self):
        self.save_user_to_db('andrew','andrew@a.com','P@ssword')
        with patch('authors.apps.authentication.social.twitter_token_validator.TwitterValidate.validate_twitter_token') as mock_twitter_validate:
            mock_twitter_validate.return_value = {
                "name": "andrew", "email": "andrew@a.com", "id_str": "104383024388008549815"}
            res = self.client.post(
                '/api/users/twitter/', {"token": "valid token for twitter"}, format='json')
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST,
                                "Response status should be 400 BAD REQUEST")
            self.assertEqual(json.loads(res.content), {"errors": {
                             "auth_token": ["Failed to register the user. Email already exists in the database"]}})
