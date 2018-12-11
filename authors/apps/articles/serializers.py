from django.contrib.auth import authenticate
from rest_framework import serializers
from ..authentication.models import User
from ..profiles.serializers import ProfileSerializer

from .models import(
    Article,
)


class CreateArticleViewSerializer(serializers.ModelSerializer):
    # author = serializers.SerializerMethodField()
    author = ProfileSerializer(read_only=True)

    # user_id = User.pk

    # def get_author(self, article):
    #     print('%%%%%%%%%%%%%%%%%', article.author)
    #     # current_user = User.objects.all().filter(
    #     #     email=request.user).values()[0]
    #     # user_id = current_user.id
    #     # profile = Profile.objects.get(user__id=user_id)
    #     # profile.bio = bio
    #     # profile.image = image
    #     # print("&&&&&&&&&&&&", self.user_id)
    #     # user = {
    #     #     "username": article.author.username,
    #     #     "bio": profile.bio,
    #     #     "image": profile.image
    #     # }
    #     return article

    class Meta:
        model = Article
        """
        List all of the fields that could possibly be included in a request
        or response, this includes fields specified explicitly above.
        """
        fields = ['id', 'title', 'body', 'description', 'image',
                  'author', 'slug', 'published', 'created_at']

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
            if len(title) > 400:
                raise serializers.ValidationError(
                    'Titles are restricted to 200 characters'
                )
