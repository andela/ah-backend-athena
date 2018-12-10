from django.db import models
from django.conf import settings


class Profile(models.Model):
    """
    This model defines a one to one relationship between a user and a profile

    """
    user = models.OneToOneField(
        'authentication.User', on_delete=models.CASCADE
    )
    bio = models.TextField(blank=True)
    image = models.URLField(blank=True)

    def __str__(self):
        return self.user.username
