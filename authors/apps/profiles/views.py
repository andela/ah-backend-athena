from ..authentication.backends import JWTAuthentication
from .exceptions import *
from .renderers import ProfileJSONRenderer
from django.shortcuts import render
from .models import Profile, Follow
from authors.apps.authentication.models import User
import json

from rest_framework import status
from rest_framework.generics import RetrieveAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .serializers import (ProfileSerializer, 
FollowSerializer, 
FollowingSerializer, 
FollowerSerializer,
)


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

class FollowAPIView(GenericAPIView):
    """
    api view handles following/unfollowing a user
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = FollowSerializer

    def is_following(self, follower, followed):
        """
        This method returns a boolean after checking if 'follower' is following the 'followed'
        """
        try:
            Follow.objects.get(
                followed=followed.pk, follower=follower.pk)
            return True
        except Follow.DoesNotExist:
            return False

    def post(self, request, *args, **kwargs):
        follower = JWTAuthentication().authenticate(request)[0]
        username = self.kwargs['username']

        try:
            followed = User.objects.get(username=username)
        except User.DoesNotExist:
            raise UserDoesNotExist

        if self.is_following(follower, followed):
            raise FollowingAlreadyException
        if follower.pk == followed.pk:
            raise FollowSelfException

        serializer_data = {"followed": followed.pk,
                           "follower": follower.pk}
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        profile = Profile.objects.get(user_id=followed.pk)
        response = {
            "username": followed.username,
            "bio": profile.bio,
            "image": profile.image,
            "following": self.is_following(follower, followed)
        }
        return Response(response, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        follower = JWTAuthentication().authenticate(request)[0]
        username = self.kwargs['username']
        try:
            followed = User.objects.get(username=username)
            following = Follow.objects.get(
                followed=followed.pk, follower=follower.pk)
            following.delete()
        except Follow.DoesNotExist:
            FollowDoesNotExist.not_following_user(username)
            raise FollowDoesNotExist

        profile = Profile.objects.get(user_id=followed.pk)
        response = {
            "username": followed.username,
            "bio": profile.bio,
            "image": profile.image,
            "following": self.is_following(follower, followed)
        }

        return Response(response, status=status.HTTP_202_ACCEPTED)


class FollowingAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = FollowingSerializer

    def get(self, request, *args, **kwargs):
        """
        this method returns a list of all users/authors that a
        user (usually the current user) is following
        """
        follower = JWTAuthentication().authenticate(request)[0]
        serializer_data = {"follower": follower.pk}
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)

        followed_by_self = Follow.objects.filter(follower=follower)
        if followed_by_self.count() == 0:
            raise NoFollowingException
        profiles = []
        for follow_object in followed_by_self:
            profile = Profile.objects.get(user_id=follow_object.followed_id)
            user = User.objects.get(id=follow_object.followed_id)
            profiles.append({
                'username': user.username,
                'bio': profile.bio,
                'image': profile.image,
                'following': True
            })
        res = {"following": profiles}
        return Response(res, status=status.HTTP_200_OK)


class FollowersAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = FollowingSerializer

    def is_following(self, follower, followed):
        """
        This method returns a boolean after checking if 'follower' is following the 'followed'
        """
        try:
            Follow.objects.get(
                followed=followed, follower=follower)
            return True
        except Follow.DoesNotExist:
            return False

    def get(self, request, *args, **kwargs):
        """
        this method returns a list of all users/authors that follow a specific user
        (usually the current user)
        """
        followed = JWTAuthentication().authenticate(request)[0]
        serializer_data = {"follower": followed.pk}
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)

        following_self = Follow.objects.filter(followed=followed)
        if following_self.count() == 0:
            raise NoFollowersException

        profiles = []
        for follow_object in following_self:
            profile = Profile.objects.get(user_id=follow_object.follower_id)
            user = User.objects.get(id=follow_object.follower_id)
            profiles.append({
                'username': user.username,
                'bio': profile.bio,
                'image': profile.image,
                'following': self.is_following(follow_object.follower_id, followed)
            })
        res = {"followers": profiles}

        return Response(res, status=status.HTTP_200_OK)


class ListProfilesView(RetrieveAPIView):
    """
    Lists the profiles of all authors in the system.
    """
    permission_classes = (IsAdminUser,)
    serializer_class = ProfileSerializer

    def retrieve(self, request):

        profile = Profile.objects.all()
        serializer = self.serializer_class(profile, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


