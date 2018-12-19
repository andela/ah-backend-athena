import json
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from ..models import Profile
from ...authentication.models import User
from ...authentication.views import VerifyAccount, RegistrationAPIView


class TestCommentLike(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = {
            'user': {
                'email': "soko@gmail.com",
                'username': "soko",
                'password': 'Sokosok1!'
            }
        }
        self.comment = {
            "comment": {
                "comment_body": "Hey, nooo"	
                        }
                } 

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

    def create_testing_user(self):
        self.client.post('/api/users/', self.user, format='json')
        request = APIRequestFactory().post(
            reverse("registration")
        )
        user = User.objects.get()
        token, uidb64 = RegistrationAPIView.generate_activation_link(
            user, request, send=False)
        self.verify_account(token, uidb64)
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        token = response.data['token']
        return token

    def create_testing_article(self):
        article = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
                "images": [{"image_url": "http://www.andela.com",
                            "image_description": "jsjjsjs"
                            }]
            }
        }

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        response = self.client.post(
            '/api/articles/', article, format='json')
        slug = response.data['slug']
        res =self.client.post(
            '/api/articles/'+slug+"/comments/", self.comment, format='json')
        return {"slug":slug,"id":res.data['id']}

    def test_like_existing_comment(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        data = self.create_testing_article()
        
        slug = data['slug']
        id = data['id']
        url = '/api/articles/{}/comments/{}/like'.format(slug,id)
        response = self.client.post(str(url), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['comment']['id'],
            id
        )

    def test_like_non_existing_comment(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        data = self.create_testing_article()
        
        slug = data['slug']
        id = 100
        url = '/api/articles/{}/comments/{}/like'.format(slug,id)
        response = self.client.post(str(url), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data['error']['body'][0],
            'Comment or article doesnot exist'
        )

    def test_dislike_non_existing_comment(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        data = self.create_testing_article()
        
        slug = data['slug']
        id = 100
        url = '/api/articles/{}/comments/{}/like'.format(slug,id)
        response = self.client.delete(str(url), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data['error']['body'][0],
            'Comment or article doesnot exist'
        )

    def test_like_existing_already_liked_comment(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        data = self.create_testing_article()
        slug = data['slug']
        id = data['id']
        url = '/api/articles/{}/comments/{}/like'.format(slug,id)
        self.client.post(str(url), format='json')
        response = self.client.post(str(url), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['comment']['id'],
            id
        )
    
    def test_dislike_existing_comment(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        data = self.create_testing_article()
        slug = data['slug']
        id = data['id']
        url = '/api/articles/{}/comments/{}/like'.format(slug,id)
        response = self.client.delete(str(url), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['comment']['id'],
            id
        )

    def test_dislike_existing_already_liked_comment(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.create_testing_user())
        data = self.create_testing_article()
        slug = data['slug']
        id = data['id']
        url = '/api/articles/{}/comments/{}/like'.format(slug,id)
        self.client.post(str(url), format='json')
        response = self.client.post(str(url), format='json')
        response = self.client.delete(str(url), format='json')
        response = self.client.post(str(url), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['comment']['id'],
            id
        )
