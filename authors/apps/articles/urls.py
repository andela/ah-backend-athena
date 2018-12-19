from django.urls import path
from rest_framework.routers import DefaultRouter


from .views import(
    CreateArticleView,
    RetrieveArticlesAPIView,
    ArticleTagsAPIView,
    ArticleDeleteAPIView,
    FavouritesView,
    LikeArticleView,
    ReadingView
)

urlpatterns = [
    path('articles', RetrieveArticlesAPIView.as_view(),),
    path('articles/<str:slug>/like/',
         LikeArticleView.as_view(), name='article-like'),
    path('articles/<str:slug>/', CreateArticleView.as_view()),
    path('articles/<slug>/<count>', ReadingView.as_view(), name='reading'),
    path('articles/', CreateArticleView.as_view(), name='article-create'),
    path('<slug>/tags/', ArticleTagsAPIView.as_view(), name='article-tags'),
    path('<slug>/tags/<tag>/', ArticleDeleteAPIView.as_view(), name='delete-tag'),
    path('articles/<slug>/favorite/', FavouritesView.as_view())
]
