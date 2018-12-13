from django.shortcuts import render
from .models import Profile
from authors.apps.authentication.models import User
import json

from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import ProfileSerializer
from .models import Profile
from .renderers import ProfileJSONRenderer
from .exceptions import ProfileDoesNotExist


class ProfileRetrieveView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    renderer_classes = (ProfileJSONRenderer,)

    def retrieve(self, request, *args, **kwargs):
        username = self.kwargs['slug']

        try:
            profile = Profile.objects.select_related('user').get(
                user__username=username
            )
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        serializer = self.serializer_class(profile)

        return Response(serializer.data, status=status.HTTP_200_OK)
