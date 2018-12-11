from django.shortcuts import render
from rest_framework import status, exceptions
from rest_framework.generics import(
    GenericAPIView
)

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.template.defaultfilters import slugify

from ..authentication.backends import JWTAuthentication
from ..authentication.models import User

from .serializers import(
    CreateArticleViewSerializer,


)


class createArticleView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    # renderer_classes= (Someserializer) Customize serializer for this app
    serializer_class = (CreateArticleViewSerializer,)

    def post(self, request):
        """ The post method is used to create articles"""
        article = request.data.get('article', {})
        """
        call the JWTAuthentication class to decode token 
        and retrieve user data
        """
        user_info = JWTAuthentication.authenticate()
        article['author'] == user_infol[1]

        """create slug from an artical"""
        if article['slug'] == '':
            try:
                slug = slugify(article['title']).replace('_', '-')
                article['slug'] = slug
            except KeyError:
                pass

        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=user_data[0])
        data = serializer.data
        data["message"] = "Article created successfully."
