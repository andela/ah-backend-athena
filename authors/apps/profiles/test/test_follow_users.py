"""
This test suite covers all the tests for the 'follow a user' feature
"""

import json
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from ...authentication.models import User
from ..models import Follow


class TestFollowUser(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.andrew = self.save_user(
            'andrew', 'andrew@a.com', 'P@ssword23lslsn')
        self.maria = self.save_user('maria', 'maria@a.com', 'P@ssword23lslsn')
        self.juliet = self.save_user(
            'julie', 'juliet@a.com', 'P@ssword23lslsn')
        self.roni = self.save_user('roni', 'roni@a.com', 'P@ssword23lslsn')
        self.sama = self.save_user('sama', 'samantha@a.com', 'P@ssword23lslsn')

    def save_user(self, username, email, pwd):
        validated_data = {'username': username,
                          'email': email, 'password': pwd}
        return User.objects.create_user(**validated_data)

    def return_verified_user_object(self, username='athena',
                                    email='athena@a.com', password='P@ssword23lslsn'):
        user = self.save_user(username, email, password)
        return user

    def test_user_trying_to_follow_is_not_authenticated(self):
        res = self.client.post('/api/profiles/sama/follow')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(res.content), {'profile': {
            'detail': 'Authentication credentials were not provided.'}})

    def test_user_followed_correctly(self):
        verified_user = self.return_verified_user_object()
        jwt = verified_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + jwt)
        res = self.client.post(
            '/api/profiles/maria/follow')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(res.content), {'profile': {
            'username': 'maria', 'bio': '', 'image': '', 'following': True}})

    def test_user_cannot_follow_self(self):
        verified_user = self.return_verified_user_object()
        jwt = verified_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + jwt)
        res = self.client.post(
            '/api/profiles/{}/follow'.format(verified_user.username))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(res.content), {'profile': {
            'detail': 'You can not follow yourself.'}})

    def test_user_follow_target_does_not_exist(self):
        verified_user = self.return_verified_user_object()
        jwt = verified_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + jwt)
        res = self.client.post(
            '/api/profiles/josephine/follow')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_already_followed(self):
        verified_user = self.return_verified_user_object()
        jwt = verified_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + jwt)
        self.client.post('/api/profiles/maria/follow')
        res = self.client.post(
            '/api/profiles/maria/follow')
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(json.loads(res.content), {'profile': {
            'detail': 'You are already following this user.'}})

    def test_user_not_following_anyone(self):
        verified_user = self.return_verified_user_object()
        jwt = verified_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + jwt)
        res = self.client.get('/api/profiles/following')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(res.content), {'profile': {
            'detail': 'You are not following any users yet.'}})

    def test_get_all_following(self):
        verified_user = self.return_verified_user_object()
        jwt = verified_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + jwt)
        follow = Follow()
        follow.follower_id = verified_user.pk
        follow.followed_id = self.andrew.pk
        follow.save()

        res = self.client.get('/api/profiles/following')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(res.content), {'profile': {'following': [
            {'username': 'andrew', 'bio': '', 'image': '', 'following': True}]}})

    def test_get_all_followers(self):
        verified_user = self.return_verified_user_object()
        jwt = verified_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + jwt)
        follow = Follow()
        follow.followed_id = verified_user.pk
        follow.follower_id = self.roni.pk
        follow.save()

        res = self.client.get('/api/profiles/followers')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(res.content), {'profile': {'followers': [
            {'username': 'roni', 'bio': '', 'image': '', 'following': True}]}})

    def test_user_has_no_followers(self):
        verified_user = self.return_verified_user_object()
        jwt = verified_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + jwt)
        res = self.client.get('/api/profiles/followers')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(res.content), {'profile': {
            'detail': 'You do not have any followers.'}})

    def test_user_unfollows(self):
        verified_user = self.return_verified_user_object()
        jwt = verified_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + jwt)
        self.client.post('/api/profiles/maria/follow')
        res = self.client.delete(
            '/api/profiles/maria/follow')
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(json.loads(res.content), {'profile': {
            'username': 'maria', 'bio': '', 'image': '', 'following': False}})

    def test_user_unfollows_non_followed_user(self):
        verified_user = self.return_verified_user_object()
        jwt = verified_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + jwt)
        res = self.client.delete(
            '/api/profiles/maria/follow')
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(json.loads(res.content), {'profile': {
            'detail': 'You are not following this user.'}})
