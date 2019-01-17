import json
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status


class TestPasswordReset(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = {
            "user": {
                "email": "lugjosh@gmail.com"
            }
        }
        self.password = {
            "password": "asdfqwerty",
            "confirm_password": "asdfqwerty"
        }
        self.user = {
            "user": {
                'email': "lugjosh@gmail.com",
                'username': "joshua",
                'password': "password1A"
            }
        }

    def logged_in_user(self):
        user = self.client.post('/api/users/', self.user, format='json')
        return user

    def test_password_reset_email(self):
        """
        test when user enters correct email
        """
        TestPasswordReset.logged_in_user(self)
        res = self.client.post('/api/password_reset/',
                               self.email, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            json.loads(res.content),
            {
                "message": "An email has been to this email"
            }
        )

    def test_password_reset_email_wrong_email(self):
        self.wrong_email = {
            "user": {
                "email": "lugjosh@me.com"
            }
        }
        TestPasswordReset.logged_in_user(self)
        res = self.client.post('/api/password_reset/',
                               self.wrong_email, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(res.content),
            {
                'errors': {
                    'email': [
                        'User with this email is not found'
                    ]
                }
            }
        )

    def test_password_reset_email_no_email(self):
        self.no_email = {
            "user": {
                "email": ""
            }
        }
        TestPasswordReset.logged_in_user(self)
        res = self.client.post('/api/password_reset/',
                               self.no_email, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(res.content),
            {
                'errors': {
                    'email': [
                        'This field may not be blank.'
                    ]
                }
            }
        )

    def test_new_password(self):
        TestPasswordReset.logged_in_user(self)
        res = self.client.put(
            '/api/password_reset_confirm/51w-49cb6dc22991ef3691de-bHVnam9zaA',
            self.password,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            json.loads(res.content),
            {
                'message': {
                    'detail': [
                        'Password successfully reset'
                    ]
                }
            }
        )

    def test_get_new_password(self):
        TestPasswordReset.logged_in_user(self)
        res = self.client.get(
            '/api/password_reset_confirm/51w-49cb6dc22991ef3691de-bHVnam9zaA',
            self.password,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_new_short_password(self):
        self.short_password = {
            "password": "qwer",
            "confirm_password": "qwer"
        }
        TestPasswordReset.logged_in_user(self)
        res = self.client.put(
            '/api/password_reset_confirm/51w-49cb6dc22991ef3691de-bHVnam9zaA',
            self.short_password,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(res.content),
            {
                'errors': {
                    'password': [
                        'Ensure this field has at least 8 characters.'
                    ],
                    'confirm_password': [
                        'Ensure this field has at least 8 characters.'
                    ]
                }
            }
        )

    def test_unequal_password(self):
        self.short_password = {
            "password": "qwerty",
            "confirm_password": "qwer"
        }
        TestPasswordReset.logged_in_user(self)
        res = self.client.put(
            '/api/password_reset_confirm/51w-49cb6dc22991ef3691de-bHVnam9zaA',
            self.short_password,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(res.content),
            {
                'errors': {
                    'body': [
                        'passwords do not match'
                    ]
                }
            }
        )

    def test_no_new_password(self):
        self.short_password = {
            "password": "",
            "confirm_password": ""
        }
        TestPasswordReset.logged_in_user(self)
        res = self.client.put(
            '/api/password_reset_confirm/51w-49cb6dc22991ef3691de-bHVnam9zaA',
            self.short_password,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(res.content),
            {
                'errors': {
                    'password': [
                        'This field may not be blank.'
                    ],
                    'confirm_password': [
                        'This field may not be blank.'
                    ]
                }
            }
        )

    def test_no_new_password_invalid_link(self):
        TestPasswordReset.logged_in_user(self)
        res = self.client.put(
            '/api/password_reset_confirm/51w-49cb6dc22991ef3691de-bHVnam9zaApollnjasadfd',
            self.password,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(res.content),
            {
                'error': {
                    'detail': [
                        'Sorry, this link is invalid'
                    ]
                }
            }
        )
