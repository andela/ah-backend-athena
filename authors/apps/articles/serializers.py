from django.contrib.auth import authenticate
from rest_framework import serializers
from ..authentication.models import User

from .models import(
    Article,
)


class CreateArticleViewSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    user_id = User.pk

    def get_author(self, request):
        author = {
            "username": article.author.username,
            "bio": article.author.profile.bio,
            "image": article.author.profile.image
        }
        return author

    class Meta:
        model = Article
        """
        List all of the fields that could possibly be included in a request
        or response, this includes fields specified explicitly above.
        """
        fields = ['id', 'title', 'body', 'description',
                  'author', 'slug', 'published', 'created_at', ]

        """
        Overide the validate methods to include validatiosn for 
        different fields
        """

        def validate_title(self, tittle):
            if len(title) > 200:
                raise serializers.ValidationError(
                    'Titles are restricted to 200 characters'
                )

        def validate_description(self, description):
            if len(title) > 400:
                raise serializers.ValidationError(
                    'Titles are restricted to 200 characters'
                )
