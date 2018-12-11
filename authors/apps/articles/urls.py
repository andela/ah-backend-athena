from django.urls import path

from .views import(
    CreateArticleView,
    CommentView,
    RepliesView
)

urlpatterns = [
    path('articles/', CreateArticleView.as_view(), name='article-create'),
    path('articles/<slug>/comments/', CommentView.as_view(), name='comment'),
    path('articles/comments/<id>', CommentView.as_view(), name='edit_comment'),
    path('articles/comments/reply/', RepliesView.as_view(), name='reply')
]
