from django.shortcuts import render
from .models import Profile
from authors.apps.authentication.models import User
import json

from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import ProfileSerializer
from .models import Profile 

class ProfileRetrieveView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProfileSerializer

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
