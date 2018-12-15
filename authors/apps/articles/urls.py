from django.urls import path

from .views import(
    CreateArticleView,
    CommentView,
    RepliesView,
    ListAuthArticlesAPIView,
    RetrieveArticlesAPIView,
    ReadingView
)

urlpatterns = [
    path('articles/<slug>/<count>', ReadingView.as_view(), name='reading'),
    path('articles/<slug>/', CreateArticleView.as_view(), name='article'),
    path('articles/', CreateArticleView.as_view(), name='article-create'),
    path('articles', RetrieveArticlesAPIView.as_view(), name='article-create'),
    path('articles/comments/reply/<id>', RepliesView.as_view(), name='edit_reply'),
    path('articles/comments/<id>', CommentView.as_view(), name='edit_comment'),
    path('articles/<slug>/comments/', CommentView.as_view(), name='comment'),
    path('articles/<commentId>/reply/', RepliesView.as_view(), name='reply')
]
