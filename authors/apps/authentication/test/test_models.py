import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import APITestCase, APIClient
from ..models import UserManager, User
from authors.apps.articles.models import Readings, Article, Comments
from authors.apps.profiles.models import Follow


class TestUsers(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='', email='', password='')
        self.supper = User.objects.create_superuser(
            username='henry', email='antena@andela.com', password='longpass')
        self.create_article = Article.objects.create(
            title='hello', )
        self.comment = Comments.objects.create(
            comment_body='hello', author=self.user, article=self.create_article)
        self.reading = Readings.objects.create(
            author=self.user, article=self.create_article, read_count=1)
        self.follow = Follow.objects.create(follower=self.user, followed=self.user)

    
    def test_readings(self):
        self.assertTrue(self.reading)
        self.assertEqual(self.reading.read_count, 1)

    def test_comment_model(self):
        self.assertEqual(str(self.comment), "hello")
        self.follow = Follow.objects.create(follower=self.user, followed=self.user)

    def test_follower_model(self):
        self.assertIn(
            'User with id: ', str(self.follow))

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

    def test_print_readings_returns_correct_format(self):
        self.assertEqual(str(self.reading), "article_id: hello, author: , views: 1")
