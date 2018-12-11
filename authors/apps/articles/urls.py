from django.urls import path
<<<<<<< HEAD
from rest_framework.routers import DefaultRouter

=======
>>>>>>> feat(articles) user can favorite article

from .views import(
    CreateArticleView,
    RetrieveArticlesAPIView,
<<<<<<< HEAD
    ArticleTagsAPIView,
    ArticleDeleteAPIView
)

urlpatterns = [
    path('articles/', CreateArticleView.as_view()),
    path('articles', RetrieveArticlesAPIView.as_view(),),
    path('articles/<str:slug>/', CreateArticleView.as_view()),
    path('articles/', CreateArticleView.as_view(), name='article-create'),
    path('<slug>/tags/',ArticleTagsAPIView.as_view(), name='article-tags'),
    path('<slug>/tags/<tag>/', ArticleDeleteAPIView.as_view(), name='delete-tag' )
]
=======
    FavouritesView
)

urlpatterns = [
    path('articles', RetrieveArticlesAPIView.as_view(), name='article-create'),
    path('articles/', CreateArticleView.as_view()),
    path('articles/<str:slug>/', CreateArticleView.as_view()),
    path('articles/<slug>/favorite/', FavouritesView.as_view())
]
>>>>>>> feat(articles) user can favorite article
