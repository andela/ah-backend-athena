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
    Favourites, Likes,
    Readings,
    Bookmarks,
    ReportArticle,
    Ratings
)


class ArticleImgSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArticleImg
        fields = ['id', 'image_url', 'description']


class CreateArticleViewSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    tagList = TagField(many=True, required=False, source='tags')
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
        fields = ['id', 'title', 'body', 'description', 'tagList',
                  'author', 'slug', 'published', 'created_at', 'updated_at',
                  'favourited', 'favouriteCount', 'likes_count', 'like',
                  'facebook_shares', 'twitter_shares', 'email_shares', 'avg_rating',
                  'read_time', 'view_count', 'read_count']

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


class ArticleImgSerializer(serializers.ModelSerializer):
    image_url = serializers.URLField()
    description = serializers.CharField()

    class Meta:
        model = ArticleImg
        fields = ['image_url', 'description',
                  'position_in_body_before', 'article', ]


class UpdateRetrieveArticleViewSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    tagList = TagField(many=True, required=False, source='tags')

    class Meta:
        model = Article
        """
        List all of the fields that could possibly be included in a request
        or response, this includes fields specified explicitly above.
        """
        fields = ['id', 'title', 'body', 'description', 'tagList',
                  'author', 'slug', 'published', 'created_at', 'updated_at', ]


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


class ReadingSerializer(serializers.ModelSerializer):
    read_time = serializers.IntegerField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    view_count = serializers.IntegerField(read_only=True)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        article = Article.objects.all().filter().values()[0]
        response['read_count'] = article['read_count']
        response['read_time'] = article['read_time']
        response['view_count'] = article['view_count']
        response['likes_count'] = article['likes_count']
        response['article'] = article['title']
        return response

    class Meta:
        model = Readings
        fields = ['read_time', 'article',
                  'likes_count', 'view_count', 'read_count']


class BookmarkSerializers(serializers.ModelSerializer):
    def to_representation(self, instance):
        response = super().to_representation(instance)
        return response

    class Meta:
        model = Bookmarks
        fields = ['id', 'article', 'profile', 'article_slug']


class ReportArticleSerializer(serializers.ModelSerializer):
    reported_by = ProfileSerializer(read_only=True)
    reported_at = serializers.DateTimeField(read_only=True)
    reason = serializers.CharField()

    class Meta:
        model = ReportArticle
        fields = ['article_id', 'article_slug',
                  'reported_by', 'reason', 'reported_at', ]


class FacebookShareSeriaizer(serializers.ModelSerializer):
    """
    This class increments number of shares for an article via the facebook platform
    """


class TwitterShareSeriaizer(serializers.ModelSerializer):
    """
    This class increments number of shares for an article via the facebook platform
    """


class EmailShareSeriaizer(serializers.ModelSerializer):
    """
    This class increments number of shares for an article via the facebook platform
    """


class RatingSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=False)

    class Meta:
        model = Ratings
        fields = ['article', 'user_id', 'rating']


class TagsAllSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'tag', 'slug']
