from django.db import models
from django.conf import settings
from ..authentication.models import User


class Profile(models.Model):
    """
    This model defines a one to one relationship between a user and a profile

    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    image = models.URLField(blank=True)

    def __str__(self):
        return self.user.username


class Follow(models.Model):
    """
    This model defines a many to many relationship between a 
    user and a 'followed', another user they are following
    It also defines a follower i.e. the user doing the following
    """
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower_user_id', null=True)
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followed_user_id', null=True)

    def __str__(self):
        return "User with id: {} follows user with id: {}".format(self.follower.pk,
                                                                  self.followed.pk)
