
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

)

def get_object(obj_class, Id):
    try:
        return obj_class.objects.get(pk=Id)
    except obj_class.DoesNotExist:
        return Response({"message": "object does not exists"}, Http404)

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

        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=profile)
        print("#####################", serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, slug):
        """
         This class method is used retrieve article by id
        """
        print(slug)
        try:
            article = Article.objects.filter(
                slug=slug
            ).first()
        except Article.DoesNotExist:
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
        serializer.save(author= user_data[0])
        data = serializer.data
        
        data["message"] = "Article created successfully."


class CommentView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer
    # renderer_classes = (CommentJSONRenderer, )

    def post(self, request, **kwargs):
        comment = request.data.get('comment', {})
        try:
            slug = self.kwargs['slug']
            article = Article.objects.get(slug=slug)
            
            author = request.user
            comment['author'] = author.id
            comment['article'] = article.id
            serializer = self.serializer_class(data=comment)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=201)
        except:
            return Response(
                {"message": "Sorry, article does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        comment = request.data.get('comment', {})
        try:
            Id = kwargs['id']
            comment_obj = get_object(Comment, Id)
            comment['author'] = request.user.id
            serializer = self.serializer_class(comment_obj, data=comment)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except:
            return Response(
                {
                    "message":
                    "Failed to update, comment or article doesnot exist"},
                    status=status.HTTP_404_NOT_FOUND
            )


    def delete(self, request, **kwargs):
        try:
            comment_obj = Comment.objects.get(id=kwargs['id'])
            comment_obj.delete()
            return Response(
                {"message": "Comment deleted successfully"}, status=status.HTTP_200_OK)
        except:
            return Response(
                {"message": "Can not delete, comment does not exist"}, status=status.HTTP_400_BAD_REQUEST)


class RepliesView(GenericAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = RepliesSerializer

    def post(self, request, commentId):
        reply = request.data.get('reply', {})
        try:
            comment = Comment.objects.get(id=commentId)
            author = request.user
            reply['author'] = author.id
            reply['comment'] = comment.id
            serializer = self.serializer_class(data=reply)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=201)
        except:
            return Response({"message": "Comment not found"})

    def put(self, request, id):
        reply = request.data.get('reply', None)
        try:
            reply_obj = get_object(Replies, id)
            author = request.user
            reply['author'] = author.id
            serializer = self.serializer_class(reply_obj, data=reply)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=200)
        except:
            return Response({
                "errors":{
                "body": [
                "can't update, reply not found"
                ]
            }})

    def delete(self, request, id):
        try:
            reply_obj = Replies.objects.get(id=id)
            reply_obj.delete()
            return Response(
                {"message": {
                    "body": ["Reply deleted successfully"]}},
                    status=status.HTTP_200_OK)
        except:
            return Response({
                "errors":{
                "body": [
                "Can't delete, reply does not exist"
                ]
            }}, status=status.HTTP_400_BAD_REQUEST)





    

        

