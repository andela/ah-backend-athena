from django.urls import path

from .views import(
    CreateArticleView,
    RetrieveArticlesAPIView
)

urlpatterns = [
    path('articles', RetrieveArticlesAPIView.as_view(), name='article-create'),
    path('articles/', CreateArticleView.as_view()),
    path('articles/<str:slug>/', CreateArticleView.as_view()),

]
