from django.urls import include, path
from django.conf.urls import url
from .views import ProfileRetrieveView
urlpatterns = [
    url('^profiles/(?P<slug>[-\w]+)$', ProfileRetrieveView.as_view(), name='profiles'),
]
