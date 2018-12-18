from datetime import datetime, timedelta
from ..authentication.models import User
from ..profiles.models import Profile
from django.db import models
from django.template.defaultfilters import slugify


class Article(models.Model):
    """
    This class implements an article model,the author field
    identifies an article with a certain user.
    """

    """Every model has a title field"""
    title = models.CharField(db_index=True, max_length=255)

    """The author field identifies an article with a certain user."""
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)

    """The body field is the actual body of the article."""
    body = models.TextField(db_index=True)

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
       An article can have many tags and the reverse is true
       """

    tags = models.ManyToManyField('articles.Tag', related_name='articles')

    """
    created at and updated at fiedls track the authors
    edit history of the article
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    """
    these fields show if the article is favourited
    and how many favourites an article has
    """
    favourited = models.BooleanField(default=False)
    favouriteCount = models.IntegerField(default=0)
    """
    this field shows how many likes an article has
    """
    likes_count = models.IntegerField(default=0)
    """
    this field shows the readtime of an article
    """
    readTime = models.IntegerField(default=0)

    objects = models.Manager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at", "-updated_at"]


class ArticleImg(models.Model):
    image_url = models.URLField(blank=True, null=True)
    description = models.CharField(db_index=True, max_length=255)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    position_in_body_before = models.IntegerField(null=True)


class Tag(models.Model):
    tag = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True, unique=True)


class Favourites(models.Model):
    """
    field contains id of user who has
    favourited an article
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    """
    this fields contains the id of the article
    being favourited
    """
    article = models.ForeignKey(
        Article, related_name="article_id", on_delete=models.CASCADE, null=True)
    """
    this fields the favourite value, either True or
    False
    """
    favourite = models.BooleanField(default=False)


class Comments(models.Model):
    """ 
    This model implements adding comments to
    the user article
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_body = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment_body

    class Meta:
        get_latest_by = ['created_at']

    def children(self):
        return Comments.objects.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True


class Likes(models.Model):
    """ 
    Adds relationship to articles
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)

    like = models.BooleanField()
