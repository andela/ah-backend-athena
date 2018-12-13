from django.urls import path

from .views import(
    CreateArticleView,
    CommentView,
    RepliesView,
    ListAuthArticlesAPIView
)

urlpatterns = [
    path('articles/comments/reply/<id>', RepliesView.as_view(), name='edit_reply'),
    path('articles/comments/<id>', CommentView.as_view(), name='edit_comment'),
    path('articles/<slug>/comments/', CommentView.as_view(), name='comment'),
    path('articles/<commentId>/reply/', RepliesView.as_view(), name='reply'),
    path('articles/<slug>', CreateArticleView.as_view(), name='article'),
    path('articles/', CreateArticleView.as_view(), name='article-create')
]
