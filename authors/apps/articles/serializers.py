from django.contrib.auth import authenticate
from rest_framework import serializers
from ..authentication.models import User

from .models import(
<<<<<<< HEAD
    Articles,
)


class CreateArticalViewSerializer(serializers.ModelSerializer):
=======
    Article,
)


class CreateArticleViewSerializer(serializers.ModelSerializer):
>>>>>>> feat(Articles): Users can can create articles
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
<<<<<<< HEAD
        model = Articles
=======
        model = Article
>>>>>>> feat(Articles): Users can can create articles
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

<<<<<<< HEAD
        def validate_description(self.description):
            if len(title) > 400:
                raise serializers.ValidationError(
                    'Descriptions are restricted to 400 characters'
=======
        def validate_description(self, description):
            if len(title) > 400:
                raise serializers.ValidationError(
                    'Titles are restricted to 200 characters'
>>>>>>> feat(Articles): Users can can create articles
                )
