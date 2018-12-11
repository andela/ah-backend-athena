from django.urls import path
<<<<<<< HEAD
from rest_framework.routers import DefaultRouter


from .views import(
    CreateArticleView,
    RetrieveArticlesAPIView,
    ArticleTagsAPIView,
    ArticleDeleteAPIView,
    FavouritesView
)

urlpatterns = [
    path('articles/', CreateArticleView.as_view()),
    path('articles', RetrieveArticlesAPIView.as_view(),),
    path('articles/<str:slug>/', CreateArticleView.as_view()),
    path('articles/', CreateArticleView.as_view(), name='article-create'),
    path('<slug>/tags/',ArticleTagsAPIView.as_view(), name='article-tags'),
<<<<<<< HEAD
    path('<slug>/tags/<tag>/', ArticleDeleteAPIView.as_view(), name='delete-tag' ),
    path('articles/<slug>/favorite/', FavouritesView.as_view())
]
=======
    path('<slug>/tags/<tag>/', ArticleDeleteAPIView.as_view(), name='delete-tag' )
]
=======

from .views import(
    createArticleView,
)

urlpatterns = [
    path('articles/', createArticleView.as_view(), name='article-create')
]
>>>>>>> feat(Articles): Users can can create articles
>>>>>>> feat(Articles): Users can can create articles
