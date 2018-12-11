from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework import status, exceptions
from ..authentication.models import User
from ..profiles.serializers import ProfileSerializer
from .relations import TagField

from .models import(

    Article,
    ArticleImg,
    Tag,
    Favourites, Likes
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
    tagList = TagField(many=True, required=False, source='tags')

    class Meta:

        model = Article

        """
        List all of the fields that could possibly be included in a request
        or response, this includes fields specified explicitly above.
        """
        fields = ['id', 'title', 'body', 'description', 'image', 'tagList',
                  'author', 'slug', 'published', 'created_at', 'updated_at', ]

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        article = Article.objects.create(**validated_data)

        for each in tags:
            article.tags.add(each)

        return article

    def update(self, instance, validated_data):

        tags = validated_data.pop('tags', [])

        instance.tags.clear()
        for tag in tags:
            instance.tags.add(tag)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance


class UpdateArticleViewSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Article
        """
        List the fields as in create articals serializer
        """
        fields = ['id', 'title', 'body', 'description', 'image',
                  'author', 'slug', 'published', ' updated_at', ' updated_at']


class TagsSerializer(serializers.ModelSerializer):
    article = serializers.SerializerMethodField()
    tags = TagField(many=True)

    class Meta:
        model = Article
        fields = ['article', 'tags']

    def get_article(self, instance):
        return instance.slug


class FavouriteSerializer(serializers.ModelSerializer):
    article = CreateArticleViewSerializer(read_only=True)

    class Meta:
        model = Favourites
        fields = [
            'article', 'favourite', 'profile'
        ]


class LikeArticleViewSerializer(serializers.ModelSerializer):
    article = CreateArticleViewSerializer(read_only=True)

    class Meta:
        model = Likes
        fields = ['id', 'article', 'profile', 'like']
