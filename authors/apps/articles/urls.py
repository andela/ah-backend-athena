from django.urls import path
from rest_framework.routers import DefaultRouter


from .views import(
    CreateArticleView,
    RetrieveArticlesAPIView,
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