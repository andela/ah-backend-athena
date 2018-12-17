from rest_framework import status, exceptions
from rest_framework.generics import(
    RetrieveUpdateAPIView,
    GenericAPIView,
    ListAPIView,
)

from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import exceptions
from .serializers import CommentSerializer, CommentDetailSerializer
from ..articles.exceptions import PermisionDenied, CommentDoesNotExist
from ..articles.models import Comments, Article
from ..articles.serializers import CreateArticleViewSerializer


class CommentView(GenericAPIView):
    """ This class allows authenticated users to comment on an article """
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

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
        except Article.DoesNotExist:
            return Response(
                   {
                    "error":{ 
                    "body": [
                        "Sorry, this article does not exist"
                    ]}},
                    status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request,slug):
        try:
            article = Article.objects.get(slug=slug)
            article_id = article.id
            comment = Comments.objects.all().filter(article_id=article_id)
            serializer = self.serializer_class(comment, many=True)
            return Response({'comments': serializer.data}, status.HTTP_200_OK)
        except Article.DoesNotExist:
             raise CommentDoesNotExist

class CommentDetailView(GenericAPIView):
    """ View class to handle child comments """
    permission_classes = (IsAuthenticated, )
    serializer_class = CommentDetailSerializer

    def get(self, request, slug, id):
        comment = Comments.objects.all().filter(id=id)
        serializer = self.serializer_class(comment, many=True)
        new_data = serializer.data 
        return Response({"comment": new_data}, status.HTTP_200_OK)

    def post(self, request, slug, id):
        comment = request.data.get('reply')
        article = get_object_or_404(Article, slug=slug)
        author = request.user
        comment['author'] = author.id
        comment['article'] = article.id
        comment['parent'] = id
        serializer = self.serializer_class(data=comment)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """ method allows the user to update his/her comment"""
        comment = request.data.get('comment', {})
        try:
            Id = kwargs['id']
            slug = kwargs['slug']
            comment_obj = Comments.objects.get(pk=Id)
            article = get_object_or_404(Article, slug=slug)
            if comment_obj.author == request.user:
                comment['author'] = request.user.id
                comment['article'] = article.id
                serializer = self.serializer_class(comment_obj, data=comment)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            else:
                raise PermisionDenied       
        except Comments.DoesNotExist:
            return Response(
                {
                    "error":{ 
                    "body":[
                        "Failed to update, comment or article doesnot exist"
                    ]}},
                    status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, **kwargs):
        """ method allows the user to delete his/her comment """
        try:
            comment_obj = Comments.objects.get(id=kwargs['id'])
            if request.user == comment_obj.author:
                comment_obj.delete()
                return Response({
                    "message":{ 
                    "body":["Comment deleted successfully"]}},
                    status=status.HTTP_200_OK)
            else:
                raise PermisionDenied
        except Comments.DoesNotExist:
            raise CommentDoesNotExist

    