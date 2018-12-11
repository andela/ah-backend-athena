from django.urls import path

from .views import(
    createArticleView,
)

urlpatterns = [
    path('articles/', createArticleView.as_view(), name='article-create')
]
