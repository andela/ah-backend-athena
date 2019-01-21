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
    description = models.CharField(db_index=True, max_length=255)

    """. The slug field makes the article searchable it can be 
    auto generated or specified by the author."""
    slug = models.SlugField(db_index=True, max_length=255, unique=True)

    """
    Published is like a draft field, helps authors to wor
    and save them to draft before publishing them
    """
    published = models.BooleanField(default=True)

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
    like = models.TextField(default='')
    read_time = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    read_count = models.IntegerField(default=0)

    """
    sharing fields: facebook_shares, twitter_shares, email_shares
    """
    facebook_shares = models.IntegerField(default=0)
    twitter_shares = models.IntegerField(default=0)
    email_shares = models.IntegerField(default=0)
    
    """
    Store the average rating for each article.
    """
    avg_rating = models.DecimalField(default=0, max_digits=3, decimal_places=1)

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

    likes_count = models.IntegerField(default=0)

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


class ComentLikes(models.Model):

    comment = models.ForeignKey(Comments, on_delete=models.CASCADE)

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)

    like = models.BooleanField()


class Readings(models.Model):
    """ model for reading stats """
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    read_count = models.IntegerField(default=0)

    def __str__(self):
        return "article_id: {}, author: {}, views: {}".format(
            self.article, self.author, self.read_count)


class Bookmarks(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    article_slug = models.CharField(max_length=225)


class ReportArticle(models.Model):
    """This class implements a model  report articles that violate
       terms of agreement
    """
    article_id = models.ForeignKey(Article, on_delete=models.CASCADE)
    article_slug = models.ForeignKey(
        Article, to_field="slug", db_column="slug", related_name='a_slug', on_delete=models.CASCADE, null=True)
    reported_by = models.ForeignKey(Profile, on_delete=models.CASCADE)
    reason = models.CharField(db_index=True, null=False, max_length=255)
    reported_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-reported_at']

class Shares(models.Model):
    """
    This class creates a model for article shares on different platforms
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    platform = models.CharField(max_length=10)
    
class Ratings(models.Model):
    """This class enables authenticated users to rate articles on a scale of 1 to 5
    and average ratings to be returned for every article. It also allows authenticated
     users to re-rate articles."""

    """We need the slug of the article that is going to be rated
       since it is unique.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    """user_id of the person who rates the article has to be stored"""
    user_id = models.IntegerField()

    """this column takes the rating/score given by a user for an article."""
    rating = models.IntegerField()
