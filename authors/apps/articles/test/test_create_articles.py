import json
from .base import BaseTestArticles
from rest_framework.views import status
from ..models import Article
from ...authentication.models import User
from ....apps.profiles.models import Profile


class TestArticles(BaseTestArticles):

    def data3_user_jwt(self):
        return User.objects.create_user(**self.data3['user']).token()
    
    def super_user_jwt(self):
        user = User.objects.create_superuser(**self.data3['user'])
        return user.token()

    def test_create_models_article(self):
        user = User.objects.create_user(
            username='henry', email='henry@gmail.com',
            password='Pass12')
        user.is_verified = True
        user = User.objects.filter(email='henry@gmail.com').first()
        author = Profile.objects.get(user_id=user.id)
        article = Article.objects.create(
            title='article title', author=author)
        self.assertEqual(str(article), article.title)

    def create_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        return response.data['slug']

    def test_create_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_article_long_title(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article_log_tile, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_article(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.get(
            '/api/articles/'+slug+'',  format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_article_doesnot_exist(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        fake_slug = "ed"*23
        response = self.client.get(
            '/api/articles/{}'.format(fake_slug),  format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_article(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.delete(
            '/api/articles/'+slug+'/',  format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_article_doesnot_exist(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        fake_slug = "ed"*23
        response = self.client.delete(
            '/api/articles/{}/'.format(fake_slug),  format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_existing_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        fake_slug = "ed"*23
        response = self.client.put(
            '/api/articles/ffhfh-ggrg/', data=self.updated_article, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_article(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.put(
            '/api/articles/'+slug+'/', data=self.updated_article, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_no_existing_published_articles(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.get(
            '/api/articles',  format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_all_published_articles(self):
        self.create_article()
        self.create_article()
        self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.get(
            '/api/articles',  format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_tags(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/', data=self.article, format='json')
        slug = self.create_article()
        response = self.client.get(
            '/api/{}/tags/'.format(slug, format='json')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tags'], ['Rails', 'Golang', 'magic!'])

    def test_delete_tag(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/', data=self.article, format='json')
        slug = self.create_article()
        response = self.client.delete(
            '/api/{}/tags/magic!/'.format(slug, format='json')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_delete_article_not_author(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/', data=self.article, format='json')
        response = json.loads(response.content)
        slug = response['article']['slug']

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.data3_user_jwt())
        res = self.client.delete(
            '/api/articles/{}/'.format(slug))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            json.loads(res.content)['article']['error'],
            'You can only delete your own articles'
        )


    def test_report_article(self):
            slug = self.create_article()
            self.client.credentials(
                HTTP_AUTHORIZATION='Bearer ' + self.login_user())
            response = self.client.post(
                '/api/articles/{}/report/'.format(slug),
                data=self.report_article_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                json.loads(response.content)['reported']['reason'],
                'article contains porn'
            )

    def test_report_article_doesnot_exist(self):
        slug = 'fake-slug'
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/{}/report/'.format(slug),
            data=self.report_article_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            json.loads(response.content)['errors'],
            'This article doesnot exist'
        )

    def test_report_article_no_data(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/{}/report/'.format(slug), data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content)['errors'],
            'Provide reason for reporting'
        )

    def test_report_article_empty_reason(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.post(
            '/api/articles/{}/report/'.format(slug),
            self.report_article_data_empty_reason, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content)['errors']['reason'],
            ['This field may not be blank.']
        )

    def test_report_article_more_than_5_times(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        for article in range(6):
            self.client.post(
                '/api/articles/{}/report/'.format(slug),
                data=self.report_article_data, format='json')
        response = self.client.post(
            '/api/articles/{}/report/'.format(slug),
            data=self.report_article_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            json.loads(response.content)['errors'],
            'This article has been reported more than 5 times'
        )

    def test_fetch_all_reported_articles_non_superuser(self):
        self.create_article()
        self.create_article()
        self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.get('/api/reported/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            json.loads(response.content)['reported']['detail'],
            'You do not have permission to perform this action.'
        )

    def test_fetch_all_reported_articles_superuser(self):
        slug1 = self.create_article()
        slug2 = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.super_user_jwt())
        self.client.post(
            '/api/articles/{}/report/'.format(slug1),
            data=self.report_article_data, format='json')
        self.client.post(
            '/api/articles/{}/report/'.format(slug2),
            data=self.report_article_data, format='json')
        response = self.client.get('/api/reported/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            slug2,
            json.loads(response.content)[
                'reported']['articles'][0]['article_slug'],
        )

    def test_fetch_all_reported_articles_that_dont_exist(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.super_user_jwt())
        response = self.client.get('/api/reported/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            json.loads(response.content)['reported']['articles']['message'],
            'There are no reported articles'
        )

    def test_revert_reported_article(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/{}/report/'.format(slug), format='json')
        self.client.post(
            '/api/articles/{}/report/'.format(slug), format='json')
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.super_user_jwt())
        response = self.client.put(
            '/api/reported/{}/revert/'.format(slug), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['reported']['message'],
            'article restored successully'
        )

    def test_revert_reported_article_doesnot_exist(self):
        slug = 'fake_slug'
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.super_user_jwt())
        response = self.client.put(
            '/api/reported/{}/revert/'.format(slug), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_reported_article(self):
        slug = self.create_article()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/{}/report/'.format(slug), format='json')
        self.client.post(
            '/api/articles/{}/report/'.format(slug), format='json')
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.super_user_jwt())
        response = self.client.delete(
            '/api/reported/{}/delete/'.format(slug), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['reported']['message'],
            'article was deleted successully'
        )

    def test_delete_reported_article_doesnot_exist(self):
        self.create_article()
        slug = 'fakeslug'
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.super_user_jwt())
        response = self.client.delete(
            '/api/reported/{}/delete/'.format(slug), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data['reported']['error'],
            'This article doesnot exist'
        )

    def test_articles_pagination(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        self.client.post(
            '/api/articles/', data=self.article, format='json')
        self.client.post(
            '/api/articles/', data=self.article, format='json')
        response = self.client.get(
            '/api/articles?page=1&limit=1',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_page_doesnot_exist(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_user())
        response = self.client.get(
            '/api/articles?page=5',format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

