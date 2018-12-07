from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Profile



class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    bio = serializers.CharField(allow_blank=True, required=False)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'bio', 'image','email')
        read_only_fields = ('username',)

    def get_image(self, obj):
        if obj.image:
            return obj.image

        return ''


