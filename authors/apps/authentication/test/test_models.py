import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import APITestCase, APIClient
from ..models import UserManager, User


class TestUsers(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='', email='', password='')
        self.supper = User.objects.create_superuser(
            username='henry', email='antena@andela.com', password='longpass')

    def test_users_is_instance_of_User(self):
        self.assertIsInstance(self.user, User)
        self.assertIsInstance(self.supper, User)

    def test_raise_type_error_no_username_details(self):
        try:
            response = User.objects.create_user(
                username=None, email='anthena@andela.com'
            )
        except TypeError as error:
            self.assertTrue(str(error), 'Users must have a username.')

    def test_user_missing_password(self):
        try:
            res = User.objects.create_user(
                username='soko', email=None
            )
        except TypeError as error:
            self.assertTrue(str(error), 'Users must have an email address.')

    def test_create_a_user_model(self):
        self.assertTrue(self.supper.username, 'henry')
        self.assertNotEqual(self.supper.username, 'kasule')
        self.assertTrue(self.supper.email, 'anthena@andela.com')
        self.assertTrue(self.user)

    def test_get_short_name_and_full_name(self):
        self.assertTrue(self.supper.get_full_name, 'henry')
        self.assertTrue(self.supper.get_short_name, 'henry')

    def test_token_created_successfully(self):
        self.assertGreater(len(User.token(self.supper)), 12)
