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
from ..articles.models import Comments, Article, ComentLikes
from ..articles.serializers import CreateArticleViewSerializer
from ..profiles.models import Profile
from ..authentication.backends import JWTAuthentication


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
                    "error": {
                        "body": [
                            "Sorry, this article does not exist"
                        ]}},
                status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, slug):
        try:
            article = Article.objects.get(slug=slug)
            article_id = article.id
            comment = Comments.objects.all().filter(article_id=article_id)
            serializer = self.serializer_class(comment, many=True)
            new_data = serializer.data
            comments_list = []
            user_id = JWTAuthentication().authenticate(request)[0].id
            profile = Profile.objects.get(user__id=user_id)
            for comm in new_data:
                comments_list.append(comm)

                liked_comments = ComentLikes.objects.filter(
                    id=comm['id']).filter(profile=profile)
                if len(liked_comments) >= 1:
                    user_like_option = liked_comments.first()
                    if user_like_option.like:

                        comm['is_like'] = True
                    else:
                        comm['is_like'] = False
                else:
                    print(comm['id'])
                    comm['is_like'] = ""
            return Response({'comments': comments_list}, status.HTTP_200_OK)
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
        comments_list = []
        user_id = JWTAuthentication().authenticate(request)[0].id
        profile = Profile.objects.get(user__id=user_id)
        for comm in new_data:
            comments_list.append(comm)

            liked_comments = ComentLikes.objects.filter(
                id=comm['id']).filter(profile=profile)
            if len(liked_comments) >= 1:
                user_like_option = liked_comments.first()
                if user_like_option.like:

                    comm['is_like'] = True
                else:
                    comm['is_like'] = False
            else:
                print(comm['id'])
                comm['is_like'] = ""
        return Response({'comments': comments_list}, status.HTTP_200_OK)

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
                    "error": {
                        "body": [
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
                    "message": {
                        "body": ["Comment deleted successfully"]}},
                    status=status.HTTP_200_OK)
            else:
                raise PermisionDenied
        except Comments.DoesNotExist:
            raise CommentDoesNotExist


class LikeCommentsView(GenericAPIView):
    """ View class to handle liking of comments """
    permission_classes = (IsAuthenticated, )
    serializer_class = CommentDetailSerializer

    def post(self, request, slug, id):
        comment_qs = Comments.objects.all().filter(id=id).filter(article__slug=slug)
        comment = comment_qs.first()
        if comment is None:
            return Response(
                {
                    "error": {
                        "body": [
                            "Comment or article doesnot exist"
                        ]}},
                status=status.HTTP_404_NOT_FOUND
            )

        user_id = JWTAuthentication().authenticate(request)[0].id
        profile = Profile.objects.get(user__id=user_id)

        liked_comments = ComentLikes.objects.filter(
            comment=comment).filter(profile=profile)
        if len(liked_comments) >= 1:
            user_like_option = liked_comments.first()
            if not user_like_option.like:
                comment.likes_count = comment.likes_count + 1
                comment.save()
            user_like_option.like = True
            user_like_option.save()
            serializer = self.serializer_class(comment, many=False)
            new_data = serializer.data
        else:
            comment.likes_count = comment.likes_count + 1
            comment.save()
            lik = ComentLikes(comment=comment, profile=profile, like=True)
            lik.save()
            serializer = self.serializer_class(comment, many=False)
            new_data = serializer.data

        return Response({"comment": new_data}, status.HTTP_200_OK)

    def delete(self, request, slug, id):
        comment_qs = Comments.objects.all().filter(id=id).filter(article__slug=slug)
        comment = comment_qs.first()
        if comment is None:
            return Response(
                {
                    "error": {
                        "body": [
                            "Comment or article doesnot exist"
                        ]}},
                status=status.HTTP_404_NOT_FOUND
            )
        user_id = JWTAuthentication().authenticate(request)[0].id
        profile = Profile.objects.get(user__id=user_id)

        liked_comments = ComentLikes.objects.filter(
            comment=comment).filter(profile=profile)

        if len(liked_comments) >= 1:
            user_like_option = liked_comments.first()
            if user_like_option.like:
                comment.likes_count = comment.likes_count - 1
                comment.save()
            user_like_option.like = False
            user_like_option.save()
            serializer = self.serializer_class(comment, many=False)
            new_data = serializer.data
        else:
            comment.likes_count = comment.likes_count - 1
            comment.save()
            lik = ComentLikes(comment=comment, profile=profile, like=False)
            lik.save()
            serializer = self.serializer_class(comment, many=False)
            new_data = serializer.data

        return Response({"comment": new_data}, status.HTTP_200_OK)
