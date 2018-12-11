from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework import status, exceptions
from ..authentication.models import User
from ..profiles.serializers import ProfileSerializer

from .models import(
    Article,
    ArticleImg
)


class ArticleImgSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArticleImg
        fields = ['id', 'image_url', 'description']


class CreateArticleViewSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    image = ArticleImgSerializer(read_only=True)
    """
    slug = serializers.SlugField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    """
    class Meta:
        model = Article
        """
        List all of the fields that could possibly be included in a request
        or response, this includes fields specified explicitly above.
        """
        fields = ['id', 'title', 'body', 'description', 'image',
                  'author', 'slug', 'published', 'created_at', 'updated_at', ]


class UpdateArticleViewSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    image = ArticleImgSerializer(read_only=False)

    class Meta:
        model = Article
        """
        List the fields as in create articals serializer
        """
        fields = ['id', 'title', 'body', 'description', 'image',
                  'author', 'slug', 'published', ' updated_at', ' updated_at']

        """
        Overide methods as in create artical serializer
        """
