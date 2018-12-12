from django.urls import path
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
    path('<slug>/tags/<tag>/', ArticleDeleteAPIView.as_view(), name='delete-tag' ),
    path('articles/<slug>/favorite/', FavouritesView.as_view())
]
<<<<<<< HEAD
=======
=======
    path('<slug>/tags/<tag>/', ArticleDeleteAPIView.as_view(), name='delete-tag' )
]
=======

from .views import(
    CreateArticleView,
    RetrieveArticlesAPIView, LikeArticleView
)

urlpatterns = [
    path('articles', RetrieveArticlesAPIView.as_view(), name='article-create'),
    path('articles/', CreateArticleView.as_view()),
    path('articles/<str:slug>/', CreateArticleView.as_view()),
    path('like/', LikeArticleView.as_view(), name='article-like'),

]
>>>>>>> feat(Articles): Users can can create articles
>>>>>>> feat(Articles): Users can can create articles
>>>>>>> feat(like_dislike): impliment like article and links to the endpoint
