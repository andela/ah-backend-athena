
import uuid, readtime
from django.shortcuts import render
from rest_framework import generics, mixins, status, viewsets
from rest_framework import status, exceptions
from rest_framework.generics import(
    RetrieveUpdateAPIView,
    GenericAPIView,
    ListAPIView,
    CreateAPIView,
    RetrieveUpdateAPIView
)

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    IsAdminUser
)
from rest_framework.response import Response
from rest_framework import exceptions
from django.template.defaultfilters import slugify
from authors.settings import RPD
from ..authentication.backends import JWTAuthentication
from ..authentication.models import User
from .renderers import ArticleJSONRenderer, ListArticlesJSONRenderer
from .models import ArticleImg, Article, Tag, Favourites, Likes, Readings, Bookmarks
from .renderers import(
    ArticleJSONRenderer,
    ListArticlesJSONRenderer,
    ArticleJSONRenderer,
    ArticleListReportJSONRenderer,
    ArticleReportJSONRenderer
)
from .models import(
    ArticleImg,
    Article,
    Tag,
    Favourites,
    Likes,
    Readings,
    ReportArticle
)

from ..profiles.models import Profile
from .pagination import StandardResultsPagination


from .serializers import(
    CreateArticleViewSerializer,
    UpdateRetrieveArticleViewSerializer,
    ArticleImgSerializer,
    TagsSerializer,
    FavouriteSerializer,
    LikeArticleViewSerializer,
    ReadingSerializer,
    BookmarkSerializers,
    ReportArticleSerializer

)


class CreateArticleView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = CreateArticleViewSerializer


    def post(self, request):
        """ The post method is used to create articles"""
        article = request.data.get('article', {})
        """
        call the JWTAuthentication class to decode token
        and retrieve usere data
        """

        image_data = article.pop('images')

        slug = slugify(article["title"]).replace("_", "-")
        slug = slug + "-" + str(uuid.uuid4()).split("-")[-1]
        article["slug"] = slug
        full_article = "{} {}".format(article['title'], article['body'])
        words = full_article.split()
        minutes = (len(words)//RPD)
        article['read_time'] = int(minutes)
        current_user = User.objects.all().filter(
            email=request.user).values()[0]
        user_id = current_user['id']
        profile = Profile.objects.get(user__id=user_id)

        """
        estimates the time an article should take to be read
        """
        article_body = article["body"]
        results = readtime.of_text(article_body)
        read_time = results.minutes
        article['read_time'] = read_time

        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=profile)

        article_ob = Article.objects.get(slug=slug)

        """
        saves the readtime value to the database
        """
        article_ob.read_time = read_time
        article_ob.save()

        for image_obj in image_data:

            images_serializer_class = ArticleImgSerializer
            images_serializer = images_serializer_class(
                data=image_obj, partial=True)
            images_serializer.is_valid(raise_exception=True)
            images_serializer.save(article=article_ob)

        image_list = ArticleImg.objects.all().filter(
            article_id=article_ob.id).values()
        res = serializer.data
        images_list = []
        for image in list(image_list):
            image.pop('article_id')
            images_list.append(image)
        res['images'] = images_list
        return Response(res, status=status.HTTP_201_CREATED)

    def get(self, request, slug):
        serializer_class = UpdateRetrieveArticleViewSerializer

        """
         This class method is used retrieve article by id
        """
        article = Article.objects.filter(
            slug=slug
        ).first()
        if not article:
            error = {"error": "This article doesnot exist"}
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(article)

        image_list = ArticleImg.objects.all().filter(
            article_id=article.id).values()
        res = serializer.data
        images_list = []
        for image in list(image_list):
            image.pop('article_id')
            images_list.append(image)
        res['images'] = images_list

        return Response(res, status=status.HTTP_200_OK)

    def delete(self, request, slug):
        serializer_class = UpdateRetrieveArticleViewSerializer

        """
        This methode deletes a user artical
        """
        user_data = JWTAuthentication().authenticate(request)
        profile = Profile.objects.get(user__id=user_data[0].id)

        try:
            article = Article.objects.get(slug=slug)

            if not (article.author_id == profile.id):

                return Response(
                    {"error": "You can only delete your own articles"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            article.delete()
        except Article.DoesNotExist:
            error = {"error": "This article doesnot exist"}
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        data = {"message": "article was deleted successully"}
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, slug):
        serializer_class = UpdateRetrieveArticleViewSerializer
        """
            This methode updates an article
        """
        try:
            article_obj = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            error = {"error": "This article doesnot exist"}
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        article = request.data.get('article', {})
        user_info = JWTAuthentication().authenticate(request)
        current_user = user_info[0]
        profile = Profile.objects.get(user__id=current_user.id)
        image_data = article['images']
        for image in image_data:
            image_obj = ArticleImg.objects.filter(
                id=image['id']
            ).first()
            img_serializer = ArticleImgSerializer(
                image_obj, data=image, partial=True)
            img_serializer.is_valid(raise_exception=True)
            img_serializer.save(article=article_obj)

        """ Create a new slug id from the title"""

        slug = slugify(article["title"]).replace("_", "-")
        slug = slug + "-" + str(uuid.uuid4()).split("-")[-1]
        article["slug"] = slug

        serializer = CreateArticleViewSerializer(
            article_obj, data=article, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=profile)

        article_ob = Article.objects.get(slug=slug)

        image_list = ArticleImg.objects.all().filter(
            article_id=article_ob.id).values()
        res = serializer.data
        images_list = []
        for image in list(image_list):
            image.pop('article_id')
            images_list.append(image)
        res['images'] = images_list

        return Response(res, status=status.HTTP_201_CREATED)


class RetrieveArticlesAPIView(GenericAPIView):
    serializer_class = UpdateRetrieveArticleViewSerializer

    permission_classes = (IsAuthenticated,)
    renderer_classes = (ListArticlesJSONRenderer,)
    pagination_class = StandardResultsPagination

    def get(self, request):
        """
         This class method is used retrieve articles
        """
        articles = Article.objects.all()
        paginated_data = self.paginate_queryset(articles)
        article_list = []
        for article in list(paginated_data):
            images = ArticleImg.objects.filter(
                article_id=article.id).values()
            article = UpdateRetrieveArticleViewSerializer(article).data
            images_list = []
            for image in list(images):
                image.pop('article_id')
                images_list.append(image)
            article['images'] = images_list
            article_list.append(article)
        if len(article_list) == 0:
            data = {'message': 'There are no articles articles'}
            return Response({"articles": data}, status=status.HTTP_404_NOT_FOUND)
        return self.get_paginated_response(article_list)

class ArticleTagsAPIView(GenericAPIView):
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        slug = kwargs['slug']
        article = Article.objects.filter(
            slug=slug
        ).first()
        serializer = CreateArticleViewSerializer(article).data
        tags = serializer["tagList"]
        return Response({
            'tags': tags
        }, status=status.HTTP_200_OK)


class ArticleDeleteAPIView(GenericAPIView):

    def delete(self, request, *args, **kwargs):
        slug = kwargs['slug']
        tag = kwargs['tag']
        article = Article.objects.filter(
            slug=slug
        ).first()
        serializer = CreateArticleViewSerializer(article).data
        tags = serializer["tagList"]
        for each in tags:
            one = Tag.objects.get(tag=tag)
            if one:
                article.tags.remove(one)

        output = TagsSerializer(article)
        return Response(output.data)


class FavouritesView(GenericAPIView):
    serializer_class = FavouriteSerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleJSONRenderer,)

    def post(self, request, **kwargs):
        user = JWTAuthentication().authenticate(request)
        user_id = user[0].id
        try:
            article_slug = kwargs['slug']
            profile = Profile.objects.get(user__id=user_id)
            article_obj = Article.objects.get(slug=article_slug)
            article_id = article_obj.id
        except:
            return Response({
                "error": {
                    "body": [
                        "article doesnot exist"
                    ]
                }
            },
                status=400
            )

        fav = Favourites.objects.filter(
            article_id=article_id
        ).filter(
            profile=profile
        )
        fav_option = fav.first()
        if fav_option:
            return Response(
                {
                    "error": {
                        "body": [
                            "article already favorited"
                        ]
                    }
                },
                status=409
            )
        else:

            serializer = self.serializer_class(data={}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(profile=profile,
                            article=article_obj, favourite=True)

            favs = Favourites.objects.filter(
                article_id=article_id
            ).filter(
                favourite=True
            )

            article_obj.favourited = True
            article_obj.favouriteCount = favs.count()
            article_obj.save()
            return Response(serializer.data, status=200)

    def delete(self, request, **kwargs):
        user = JWTAuthentication().authenticate(request)
        user_id = user[0].id
        try:
            article_slug = kwargs['slug']
            profile = Profile.objects.get(user__id=user_id)
            article_obj = Article.objects.get(slug=article_slug)
            articel_id = article_obj.id
        except:
            return Response({
                "error": {
                    "body": [
                        "article doesnot exist"
                    ]
                }
            },
                status=400
            )
        fav = Favourites.objects.filter(
            article_id=articel_id
        ).filter(
            profile=profile
        )
        if fav:
            fav.delete()
        article_obj.favourited = False
        article_obj.save()
        serializer = self.serializer_class(data={}, partial=True)
        serializer.is_valid(raise_exception=True)

        return Response({
            "message": {
                "body": [
                    "article has been unfavorited"
                ]
            }
        }, status=200)


class LikeArticleView(GenericAPIView):
    def post(self, request, slug):
        user_id = JWTAuthentication().authenticate(request)[0].id
        profile = Profile.objects.get(user__id=user_id)

        try:
            current_article = Article.objects.get(
                slug=slug)
        except Article.DoesNotExist:
            raise exceptions.NotFound(
                'This artical doesnot exist'
            )

        user_like_options = Likes.objects.filter(
            profile=profile).filter(article__slug=slug)

        if len(user_like_options) >= 1:
            user_like_option = user_like_options.first()
            if not user_like_option.like:
                current_article.likes_count = current_article.likes_count + 1
                current_article.save()
            user_like_option.like = True
            user_like_option.save()
            return Response(LikeArticleViewSerializer(user_like_option).data, status=status.HTTP_201_CREATED)
        else:
            current_article.likes_count = current_article.likes_count + 1
            current_article.save()
            serializer = LikeArticleViewSerializer(data={"like": True})
            serializer.is_valid(raise_exception=True)
            serializer.save(article=current_article, profile=profile)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, slug):
        user_id = JWTAuthentication().authenticate(request)[0].id
        profile = Profile.objects.get(user__id=user_id)

        try:
            current_article = Article.objects.get(
                slug=slug)
        except Article.DoesNotExist:
            raise exceptions.NotFound(
                'This artical doesnot exist'
            )

        user_like_options = Likes.objects.filter(
            profile=profile).filter(article__slug=slug)

        if len(user_like_options) >= 1:

            user_like_option = user_like_options.first()
            if user_like_option.like and current_article.likes_count > 0:
                current_article.likes_count = current_article.likes_count - 1
                current_article.save()
            user_like_option.like = False
            user_like_option.save()
            return Response(LikeArticleViewSerializer(user_like_option).data, status=status.HTTP_201_CREATED)
        else:
            current_article.likes_count = current_article.likes_count - 1
            current_article.save()
            serializer = LikeArticleViewSerializer(data={"like": False})
            serializer.is_valid(raise_exception=True)
            serializer.save(article=current_article, profile=profile)

            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReadingView(GenericAPIView):
    """ class view to enable viewing readers statistics """
    serializer_class = ReadingSerializer

    def do_math(self, article, count):
        """
        If the amount of time a user spends on an article is equal,
        greater than article read time, or greater 1/2 the read time
        the user is counted as to read the article. otherwise,
        the use is not counted.
        method returns True if the user is eligible to have 
        read the article and False otherwise.
        """ 
        read_time = article.read_time
        average = 0
        if int(read_time) < int(count) or int(read_time) == int(count):
            average = int(count)
        elif int(count) != 0 and int(read_time) > int(count):
            average = int(read_time) // 2
        if average >= int(read_time) or int(count) > average:
            return True
        return False

    def post(self, request, slug, count):
        """
         This class method updates the view counts on an article
        """
        article = Article.objects.filter(slug=slug).first()
        reader = Readings.objects.filter(author=request.user.id).filter(article=article)
        if not self.do_math(article, count):
            return Response({"message":"read not recorded"}, status=status.HTTP_301_MOVED_PERMANENTLY)
        if len(reader) < 1:
            article.read_count += 1
            article.save()
            author = User.objects.get(id=request.user.id)
            read_obj = Readings(author=author,article=article)
            read_obj.save()
            serializer = self.serializer_class(read_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = self.serializer_class(reader.first())
            return Response(serializer.data, status=status.HTTP_200_OK)
          

class BookmarkView(GenericAPIView):
    serializer_class = BookmarkSerializers
    permission_classes = (IsAuthenticated,)
    def post(self, request, slug):
        user_id = JWTAuthentication().authenticate(request)[0].id
        profile = Profile.objects.get(user__id=user_id)
        try:
            article = Article.objects.get(slug=slug)
            book = Bookmarks.objects.filter(profile=profile).filter(article=article)
            if len(book) < 1:
                bookmark = Bookmarks()
                bookmark ={
                    "article": article.id,
                    "profile": profile.id,
                    "article_slug": article.slug
                }
                serializer = self.serializer_class(data=bookmark)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data , status.HTTP_201_CREATED)
            return Response({"message": "article was bookmarked"}, status.HTTP_301_MOVED_PERMANENTLY)
        except:
            return Response({"error": "Article does not exist"}, status.HTTP_404_NOT_FOUND)

    def get(self, request):
        user_id = JWTAuthentication().authenticate(request)[0].id
        profile = Profile.objects.get(user__id=user_id)
        bookmark = Bookmarks.objects.all().filter(profile=profile)
        if len(bookmark) < 1:
            return Response({"message": "Bookmarks not found"}, status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(bookmark, many=True)
        new_data = serializer.data 
        return Response({"bookmark": new_data}, status.HTTP_200_OK)          

    def delete(self, request, id):
        try:
            book = Bookmarks.objects.get(id=id)
            if str(request.user.username) == str(book.profile):
                book.delete()
                return Response({"message": "Article unbookmarked"}, status.HTTP_200_OK)
            return Response({"message": "sorry, permission denied"}, status.HTTP_403_FORBIDDEN)
        except:
            return Response({"error": "bookmark does not exist"}, status.HTTP_404_NOT_FOUND)
      


class ReporteArticleAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleReportJSONRenderer,)
    serializer_class = ReportArticleSerializer

    def post(self, request, *args, **kwargs):

        user_data = JWTAuthentication().authenticate(request)
        profile = Profile.objects.get(user__id=user_data[0].id)
        slug = kwargs['slug']
        report = request.data.get('report', {})
        if report == {}:
            return Response(
                {"errors": "Provide reason for reporting"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            article_ob = Article.objects.get(
                slug=slug
            )
        except Article.DoesNotExist:
            return Response(
                {"errors": "This article doesnot exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        reported_articles = ReportArticle.objects.filter(
            article_id=article_ob.id)
        if len(list(reported_articles)) >= 5:
            article_ob.published = False
            article_ob.save()
            return Response(
                data={
                    "errors": "This article has been reported more than 5 times"
                },
                status=status.HTTP_409_CONFLICT
            )

        serializer = self.serializer_class(data=report, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            article_id=article_ob,
            article_slug=article_ob,
            reported_by=profile
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReportedArticleListAPIView(GenericAPIView):
    serializer_class = ReportArticleSerializer
    renderer_classes = (ArticleListReportJSONRenderer,)
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get(self, request):
        queryset = ReportArticle.objects.filter()
        serializer = self.serializer_class(queryset, many=True)
        data = serializer.data
        if len(data) == 0:
            data = {'message': 'There are no reported articles'}
            return Response({"articles": data},
                            status=status.HTTP_404_NOT_FOUND)
        return Response({"articles": data}, status=status.HTTP_200_OK)

    def put(self, request, slug):
        """Revert mistakenly reported articles
        """
        try:
            article = Article.objects.get(slug=slug)
            article.published = True
            article.save()
        except Article.DoesNotExist:
            error = {"error": "This article doesnot exist"}
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        reported_article = ReportArticle.objects.filter(
            article_id=article.id)
        reported_article.delete()

        data = {"message": "article restored successully"}
        return Response({"reported": data}, status=status.HTTP_200_OK)

    def delete(self, request, slug):
        """Permernebtly delete article from database which
           has been verified to violate terms
        """
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            error = {"error": "This article doesnot exist"}
            return Response({"reported": error},
                            status=status.HTTP_404_NOT_FOUND)
        article.delete()
        data = {"message": "article was deleted successully"}
        return Response({"reported": data}, status=status.HTTP_200_OK)
        


