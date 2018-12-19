from django.urls import include, path
from django.conf.urls import url
from .views import (ProfileRetrieveView, FollowAPIView, 
FollowingAPIView, 
FollowersAPIView,
ListProfilesView)

urlpatterns = [
    path('profiles/following', FollowingAPIView.as_view()),
    path('profiles/followers', FollowersAPIView.as_view()),
    url('^profiles/(?P<slug>[-\w]+)$',
        ProfileRetrieveView.as_view(), name='profiles'),
    path('profiles/<username>/follow', FollowAPIView.as_view()),
    path('profiles/', ListProfilesView.as_view()),
]
