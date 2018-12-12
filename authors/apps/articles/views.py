
import uuid
from django.shortcuts import render
from rest_framework import status, exceptions
from rest_framework.generics import(
    RetrieveUpdateAPIView,
    GenericAPIView,
    ListAPIView,
)

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import exceptions
from django.template.defaultfilters import slugify
from django.http import Http404

from ..authentication.backends import JWTAuthentication
from ..authentication.models import User
from .renderers import ArticleJSONRenderer, ListArticlesJSONRenderer, CommentJSONRenderer
from .models import ArticleImg, Article, Comment, Replies
from ..profiles.models import Profile

from .serializers import(
    CreateArticleViewSerializer,
    CommentSerializer,
    RepliesSerializer,
    UpdateArticleViewSerializer,
    ArticleImgSerializer,
)

def get_object(obj_class, Id):
    try:
        return obj_class.objects.get(pk=Id)
    except obj_class.DoesNotExist:
        return Response('object does not exist', Http404)

class CreateArticleView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleJSONRenderer,)
    # renderer_classes= (Someserializer) Customize serializer for this app
    serializer_class = CreateArticleViewSerializer

    def post(self, request):
        """ The post method is used to create articles"""
        article = request.data.get('article', {})
        """
        call the JWTAuthentication class to decode token
        and retrieve usere data
        """

        image_data = article['image']

        image_obj = ArticleImg(
            image_url=image_data['image_url'],
            description=image_data['image_description']
        )
        image_obj.save()
        img_id = ArticleImg.objects.filter(
            image_url=image_data['image_url']).first()
        article['image'] = img_id.id

        """create slug from an article"""

        try:
            slug = slugify(article["title"]).replace("_", "-")
            slug = slug + "-" + str(uuid.uuid4()).split("-")[-1]
            article["slug"] = slug

        except KeyError:

            pass
        current_user = User.objects.all().filter(
            email=request.user).values()[0]
        user_id = current_user['id']
        profile = Profile.objects.get(user__id=user_id)

        image_data = article['image']

        image_obj = ArticleImg(
            image_url=image_data['image_url'],
            description=image_data['image_description']
        )
        image_obj.save()
        image_instance = ArticleImg.objects.filter(
            image_url=image_data['image_url'],
            description=image_data['image_description']
        ).first()

        slug = slugify(article["title"]).replace("_", "-")
        slug = slug + "-" + str(uuid.uuid4()).split("-")[-1]
        article["slug"] = slug

        current_user = User.objects.all().filter(
            email=request.user).values()[0]
        user_id = current_user['id']
        profile = Profile.objects.get(user__id=user_id)

        article.pop('image')
        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=profile, image=image_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, slug):
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

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, slug):
        """
        This methode deletes a user artical
        """
        user_data = JWTAuthentication().authenticate(request)
        profile = Profile.objects.get(user__id=user_data[0].id)

        try:
            article = Article.objects.get(slug=slug)

            if not (article.author_id == profile.id):

                return Response(
                    {"error": "Yo can only delete your own articles"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Article.DoesNotExist:
            error = {"error": "This article doesnot exist"}
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        data = {"message": "article was deleted successully"}
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, slug):
        serializer_class = UpdateArticleViewSerializer
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
        image_data = article['image']

        image_obj = ArticleImg(
            image_url=image_data['image_url'],
            description=image_data['image_description']
        )
        image_obj.save()

        img_id = ArticleImg.objects.filter(
            image_url=image_data['image_url']).first()
        article['image'] = img_id.id

        """ Create a new slug id from the title"""

        slug = slugify(article["title"]).replace("_", "-")
        slug = slug + "-" + str(uuid.uuid4()).split("-")[-1]
        article["slug"] = slug

        serializer = CreateArticleViewSerializer(
            article_obj, data=article, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=profile)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ListAuthArticlesAPIView(ListAPIView):

    permission_classes = (IsAuthenticated,)
    renderer_classes = (ListArticlesJSONRenderer,)
    serializer_class = CreateArticleViewSerializer

    def get_queryset(self):

        user_data = JWTAuthentication().authenticate(request)
        profile = Profile.objects.get(user__id=user_data[0].id)
        if len(articles) == 0:
            raise ArticlesNotExist
        return articles

class RetrieveArticlesAPIView(GenericAPIView):

    permission_classes = (IsAuthenticated,)
    renderer_classes = (ListArticlesJSONRenderer,)

    def get(self, request):
        """
         This class method is used retrieve articles
        """
        article = Article.objects.all()
        article_list = []
        for art in list(article):
            article_list.append(CreateArticleViewSerializer(art).data)
        return Response(article_list, status=status.HTTP_200_OK)
        serializer.save(author= user_data[0])
        data = serializer.data
        
        data["message"] = "Article created successfully."


class CommentView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer
    # renderer_classes = (CommentJSONRenderer, )

    def post(self, request, **kwargs):
        slug = self.kwargs['slug']
        comment = request.data.get('comment', {})
        article = Article.objects.get(slug=slug)
        
        author = request.user
        comment['author'] = author.id
        comment['article'] = article.id
        serializer = self.serializer_class(data=comment)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    def put(self, request, *args, **kwargs):
        Id = kwargs['id']
        copy = get_object(Comment, Id)
        print(copy)
        comment = request.data.get('comment', {})
        comment['author'] = request.user.id
        serializer = self.serializer_class(copy, data=comment)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, **kwargs):
        comment_obj = Comment.objects.get(id=kwargs['id'])
        todelete = comment_obj
        if str(comment_obj):
            todelete.delete()
        else:
            return Response("message", "Comment deleted successfully", status=400)
        return Response(status=status.HTTP_200_OK)


class RepliesView(GenericAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = RepliesSerializer

    def post(self, request):
        reply = request.data.get('reply', {})
        comment = Comment.objects.get(id=6)
        author = request.user
        reply['author'] = author.id
        reply['comment'] = comment.id
        serializer = self.serializer_class(data=reply)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


    

        

