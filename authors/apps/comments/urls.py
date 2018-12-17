from django.urls import path

from .views import(
    CommentView,
    CommentDetailView
)
urlpatterns = [
path('articles/<slug>/comments/', CommentView.as_view(), name='comment'),
path('articles/<slug>/comments/<id>/', CommentDetailView.as_view(), name='reply'),
]
