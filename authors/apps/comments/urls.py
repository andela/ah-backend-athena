from django.urls import path

from .views import(
    CommentView,
    CommentDetailView,
    LikeCommentsView
)
urlpatterns = [
path('articles/<slug>/comments/<id>/like', LikeCommentsView.as_view(), name='like_comment'),
path('articles/<slug>/comments/', CommentView.as_view(), name='comment'),
path('articles/<slug>/comments/<id>/', CommentDetailView.as_view(), name='reply'),
]
