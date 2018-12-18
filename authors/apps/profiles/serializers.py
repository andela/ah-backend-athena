from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Profile, Follow
from ..authentication.models import User
from .exceptions import *


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    bio = serializers.CharField(allow_blank=True, required=False)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'bio', 'image', 'email')
        read_only_fields = ('username',)

    def get_image(self, obj):
        if obj.image:
            return obj.image

        return ''


class FollowSerializer(serializers.ModelSerializer):
    profile = None

    class Meta:
        model = Follow
        fields = ('follower', 'followed')


class FollowingSerializer(serializers.ModelSerializer):
    """"
    This class represents the 'get all the users I follow' serializer
    """
    class Meta:
        model = Follow
        fields = ['follower']


class FollowerSerializer(serializers.ModelSerializer):
    """
    This class represents the 'get all my followers' serializer
    """
    class Meta:
        model = Follow
        fields = ['followed']


    