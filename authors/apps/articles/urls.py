from django.urls import path

from .views import(
    CreateArticleView,
    ListAuthArticlesAPIView
)

urlpatterns = [
    path('articles/', CreateArticleView.as_view(), name='article-create'),
    path('articles/<str:slug>/', CreateArticleView.as_view()),
    path('articles/auth/', ListAuthArticlesAPIView.as_view()),
]
