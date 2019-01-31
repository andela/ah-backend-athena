from django.urls import path
from rest_framework.routers import DefaultRouter


from .views import(
    CreateArticleView,
    RetrieveArticlesAPIView,
    ArticleTagsAPIView,
    ArticleDeleteAPIView,
    FavouritesView,
    LikeArticleView,
    ReadingView,
    BookmarkView,
    ReporteArticleAPIView,
    ReportedArticleListAPIView,
    ShareArticleOnFacebookAPIView,
    ShareArticleOnTwitterAPIView,
    ShareArticleViaMailAPIView,
    RateArticle,
    SearchArticlesAPIView,
    GetOneArticle,
    TagsAPIView
)

urlpatterns = [
    path('articles/search', SearchArticlesAPIView.as_view()),
    path('articles', RetrieveArticlesAPIView.as_view()),
    path('articles/<str:slug>/like/',
         LikeArticleView.as_view(), name='article-like'),
    path('article/bookmarks/', BookmarkView.as_view()),
    path('articles/<str:slug>', GetOneArticle.as_view()),
    path('articles/<str:slug>/', CreateArticleView.as_view()),
    path('articles/<slug>/<count>', ReadingView.as_view(), name='reading'),
    path('articles/<str:slug>/bookmark/', BookmarkView.as_view()),
    path('articles/bookmark/<id>/', BookmarkView.as_view()),
    path('articles/', CreateArticleView.as_view(), name='article-create'),
    path('<slug>/tags/', ArticleTagsAPIView.as_view(), name='article-tags'),
    path('<slug>/tags/<tag>/', ArticleDeleteAPIView.as_view(), name='delete-tag'),
    path('tags', TagsAPIView.as_view(), name='all-tag'),
    path('articles/<slug>/favorite/', FavouritesView.as_view()),
    path('articles/<str:slug>/report/',
         ReporteArticleAPIView.as_view(), name='report-aticle'),
    path('reported/<str:slug>/delete/',
         ReportedArticleListAPIView.as_view(), name='delete-reported-aticle'),
    path('reported/<str:slug>/revert/',
         ReportedArticleListAPIView.as_view(), name='revert-reported-aticle'),
    path('reported/',
         ReportedArticleListAPIView.as_view(), name='reported'),
    path('articles/<slug>/share/facebook/',
         ShareArticleOnFacebookAPIView.as_view()),
    path('articles/<slug>/share/twitter/',
         ShareArticleOnTwitterAPIView.as_view()),
    path('articles/<slug>/share/email/',
         ShareArticleViaMailAPIView.as_view()),
    path('articles/<str:slug>/rate/', RateArticle.as_view(), name='rate-article')
]
