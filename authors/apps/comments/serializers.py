from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework import status, exceptions
from ..authentication.models import User
from ..articles.models import Comments, Profile, ComentLikes


class CommentSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        response = super().to_representation(instance)
        profile = Profile.objects.all().filter(
            user=instance.author).values()[0]
        response['author'] = profile
        return response

    class Meta:
        model = Comments
        fields = ('id', 'comment_body', 'likes_count',
                  'created_at', 'article', 'author', 'parent')


class ChildCommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comments
        fields = ('id', 'comment_body', 'likes_count',
                  'created_at', 'author', 'parent')


class CommentDetailSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comments
        fields = ('id', 'author', 'comment_body', 'article', 'created_at', 'likes_count',
                  'replies', 'parent')

    @staticmethod
    def get_replies(obj):
        if obj.is_parent:
            return ChildCommentSerializer(obj.children(), many=True).data
        return None


class LikeCommentSerializer(serializers.ModelSerializer):
    comment = CommentSerializer(read_only=True)

    class Meta:
        model = ComentLikes
        fields = ['id', 'comment', 'profile', 'like']
