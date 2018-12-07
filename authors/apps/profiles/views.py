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
            raise

        serializer = self.serializer_class(profile)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('data', {})
        serializer = self.serializer_class(
            request.data, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
