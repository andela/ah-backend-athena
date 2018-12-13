
import uuid
from django.shortcuts import render
from rest_framework import status, exceptions
from rest_framework.generics import(
    RetrieveUpdateAPIView,
    GenericAPIView,
    ListAPIView,
)

from .exceptions import PermisionDenied, CommentDoesNotExist
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
    """ return an object or error message if the object doesnot exist """
    try:
        return obj_class.objects.get(pk=Id)
    except obj_class.DoesNotExist:
        return Response(
            {
                "error":{ 
                "body": [
                    "object does not exists"
                ]}},
               status=status.HTTP_404_NOT_FOUND
        )

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
    """ This class allows authenticated users to comment on an article """
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer
    # renderer_classes = (CommentJSONRenderer, )

    def post(self, request, **kwargs):
        """ This method allows loged in users to comment on any article """
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            return Response(
                   {
                    "error":{ 
                    "body": [
                        "Sorry, this article does not exist"
                    ]}},
                    status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request,slug):
        serializer_class = CreateArticleViewSerializer
        slug = slug
        article = Article.objects.get(slug=slug)
        serializer = serializer_class(article)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """ method allows the user to update his/her comment"""
        comment = request.data.get('comment', {})

        try:
            Id = kwargs['id']
            comment_obj = Comment.objects.get(pk=Id)
            if comment_obj.author == request.user:
                comment['author'] = request.user.id
                serializer = self.serializer_class(comment_obj, data=comment)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            else:
                raise PermisionDenied       
        except Comment.DoesNotExist:
            return Response(
                {
                    "error":{ 
                    "body":[
                        "Failed to update, comment or article doesnot exist"
                    ]}}
            )

    def delete(self, request, **kwargs):
        """ method allows the user to delete his/her comment """
        try:
            comment_obj = Comment.objects.get(id=kwargs['id'])
            if request.user == comment_obj.author:
                comment_obj.delete()
                return Response({
                    "message":{ 
                    "body":["Comment deleted successfully"]}},
                    status=status.HTTP_200_OK)
            else:
                raise PermisionDenied
        except Comment.DoesNotExist:
            raise CommentDoesNotExist

class RepliesView(GenericAPIView):
    """ Class to allow users reply on comments """
    permission_classes = (IsAuthenticated, )
    serializer_class = RepliesSerializer

    def post(self, request, commentId):
        """ This method allows a user to create a reply on a comment """
        reply = request.data.get('reply', {})
        try:
            comment = Comment.objects.get(id=commentId)
            author = request.user
            reply['author'] = author.id
            reply['comment'] = comment.id
            serializer = self.serializer_class(data=reply)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            return Response(
                { 
                    "errors":{
                    "body": [
                    "Comment not found"
                    ]
            }}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        """ This method allows a user to edit his/her reply on a comment """
        reply = request.data.get('reply', None)
        try:
            reply_obj = Replies.objects.get(id=id)
            author = request.user
            if author == reply_obj.author:
                reply['author'] = author.id
                serializer = self.serializer_class(reply_obj, data=reply)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                raise PermisionDenied
        except Replies.DoesNotExist:
            return Response({
                "errors":{
                "body": [
                "can't update, reply not found"
                ]
            }})

    def delete(self, request, id):
        """ This method allows a user to delete his/her reply from a comment """
        try:
            reply_obj = Replies.objects.get(id=id)
            print("dkhdhjk djkj", reply_obj.author)
            print("###############", request.user)
            if request.user == reply_obj.author.id:
                reply_obj.delete()
                return Response(
                    {"message": {
                        "body": ["Reply deleted successfully"]}},
                        status=status.HTTP_200_OK)
            else:
                raise PermisionDenied
        except Replies.DoesNotExist:
            return Response({
                "errors":{
                "body": [
                "Can't delete, reply does not exist"
                ]
            }}, status=status.HTTP_400_BAD_REQUEST)





    

        

