from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework import status, exceptions
from ..authentication.models import User
from ..profiles.serializers import ProfileSerializer
from ..articles.models import  Comment, Replies, Profile

from .models import(
    Article,
    ArticleImg
)

class RepliesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Replies
        fields = '__all__'

    def to_representation(self, instance):
        resp = super().to_representation(instance)
        profile = Profile.objects.all().filter(user=3).values()[0]
        comment= Comment.objects.all().filter(id=6).values()[0]
        resp['comment'] = comment
        resp['author'] = profile
        print("#############44444444", resp)
        return resp

class CommentSerializer(serializers.ModelSerializer):

    replies = RepliesSerializer(many=True, read_only=True)
    print(replies)
    def to_representation(self, instance):
        response = super().to_representation(instance)
        profile = Profile.objects.all().filter(user=instance.author).values()[0]
        reply= Replies.objects.all().values()
        response['author'] = profile
        response['replies'] = reply
        return response

    class Meta:
        model = Comment
        fields = ('id', 'comment_body', 'created_at', 'article', 'author', 'replies')

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

        def validate_title(self, title):
            if len(title) > 200:
                raise serializers.ValidationError(
                    'Titles are restricted to 200 characters'
                )

        def validate_description(self, description):
            if len(description) > 400:
                raise serializers.ValidationError(
                    'Titles are restricted to 200 characters'
                )


class UpdateArticleViewSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)

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

        def validate_title(self, title):
            if len(title) > 200:
                raise serializers.ValidationError(
                    'Titles are restricted to 200 characters'
                )

        def validate_description(self, description):
            if len(title) > 400:
                raise serializers.ValidationError(
                    'Titles are restricted to 200 characters'
                )

        def update_article(self, article_id, data, user_id):
            try:
                article_obj = Article.objects.filter(pk=article_id)
            except:
                raise serializers.ValidationError(
                    'This artical doesnot exist'
                )

