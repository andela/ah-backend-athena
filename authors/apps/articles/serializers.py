from django.contrib.auth import authenticate
from rest_framework import serializers
from ..authentication.models import User
from ..profiles.serializers import ProfileSerializer

from .models import(
    Article,
)


class CreateArticleViewSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Article
        """
        List all of the fields that could possibly be included in a request
        or response, this includes fields specified explicitly above.
        """
        fields = ['id', 'title', 'body', 'description', 'image',
                  'author', 'slug', 'published', 'created_at', 'updated_at', ]

        """
        Overide the validate methods to include validatiosn for 
        different fields
        """

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
