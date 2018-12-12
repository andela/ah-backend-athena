from datetime import datetime, timedelta
from ..authentication.models import User
from ..profiles.models import Profile
from django.db import models


class ArticleImg(models.Model):
    image_url = models.URLField(blank=True, null=True)
    description = models.CharField(db_index=True, max_length=255)


class Article(models.Model):
    """
    This class implements an article model,the author field
    identifies an article with a certain user.
    """

    """Every modle a title ield"""
    title = models.CharField(db_index=True, max_length=255)

    """The author field identifies an article with a certain user."""
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)

    """The body field is the actual body of the article."""
    body = models.TextField(db_index=True)

    """An article can have images in the body"""
    image = models.ForeignKey(ArticleImg, on_delete=models.CASCADE)

    """A description contains what the article is about"""
    description = models.CharField(db_index=True, max_length=255, null=True)

    """. The slug field makes the article searchable it can be 
    auto generated or specified by the author."""
    slug = models.SlugField(
        db_index=True, max_length=255, unique=True, blank=False)

    """
    Published is like a draft field, helps authors to wor
    and save them to draft before publishing them
    """
    published = models.BooleanField(default=False)

    """
    created at and updated at fiedls track the authors
    edit history of the article
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at", "-updated_at"]

class Comment(models.Model):
    """ 
    This model implements adding comments to
    the user article
    """

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_body = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment_body

    class Meta:
        get_latest_by = ['created_at']



class Replies(models.Model):
    """
    Model to create a reply on the comment
    """

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    reply_body = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reply_body

    class Meta:
        ordering = ['created_at']

