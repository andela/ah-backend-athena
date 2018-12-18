from django.urls import path
from rest_framework.routers import DefaultRouter


from .views import(
    CreateArticleView,
    RetrieveArticlesAPIView,
    ArticleTagsAPIView,
    ArticleDeleteAPIView,
    FavouritesView,
    LikeArticleView,
    ReporteArticleAPIView,
    ReportedArticleListAPIView,
)

urlpatterns = [
    path('articles', RetrieveArticlesAPIView.as_view(),),
    path('articles/<str:slug>/like/',
         LikeArticleView.as_view(), name='article-like'),
    path('articles/<str:slug>/', CreateArticleView.as_view(), name='article-create'),
    path('articles/', CreateArticleView.as_view()),
    path('<slug>/tags/', ArticleTagsAPIView.as_view(), name='article-tags'),
    path('<slug>/tags/<tag>/', ArticleDeleteAPIView.as_view(), name='delete-tag'),
    path('articles/<slug>/favorite/', FavouritesView.as_view()),
    path('articles/<str:slug>/report/',
         ReporteArticleAPIView.as_view(), name='report-aticle'),
    path('reported/<str:slug>/delete/',
         ReportedArticleListAPIView.as_view(), name='delete-reported-aticle'),
    path('reported/<str:slug>/revert/',
         ReportedArticleListAPIView.as_view(), name='revert-reported-aticle'),
    path('reported/',
         ReportedArticleListAPIView.as_view(), name='reported'),

]
