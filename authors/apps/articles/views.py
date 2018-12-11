from django.shortcuts import render
from rest_framework import status, exceptions
from rest_framework.generics import(
<<<<<<< HEAD
    CreateAPIView,
    RetrieveUpdateAPIView
=======
    GenericAPIView
>>>>>>> feat(Articles): Users can can create articles
)

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.template.defaultfilters import slugify

from ..authentication.backends import JWTAuthentication
from ..authentication.models import User

from .serializers import(
<<<<<<< HEAD
    CreateArticalViewSerializer,
=======
    CreateArticleViewSerializer,
>>>>>>> feat(Articles): Users can can create articles


)


<<<<<<< HEAD
class createArticalView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    # renderer_classes= (Someserializer,) Customize serializer for this app
    serializer_class = (CreateArticalViewSerializer,)
=======
class createArticleView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    # renderer_classes= (Someserializer) Customize serializer for this app
    serializer_class = (CreateArticleViewSerializer,)
>>>>>>> feat(Articles): Users can can create articles

    def post(self, request):
        """ The post method is used to create articles"""
        article = request.data.get('article', {})
        """
        call the JWTAuthentication class to decode token 
        and retrieve user data
        """
        user_info = JWTAuthentication.authenticate()
<<<<<<< HEAD
        article['author'] == user_detail[1]
=======
        article['author'] == user_infol[1]
>>>>>>> feat(Articles): Users can can create articles

        """create slug from an artical"""
        if article['slug'] == '':
            try:
                slug = slugify(article['title']).replace('_', '-')
                article['slug'] = slug
            except KeyError:
                pass

        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
<<<<<<< HEAD
        serializer.save(author=user_info[0])

        data["message"] = "Article successfully created"

        return Response(serializer.data, status=status.HTTP_201_CREATED)
=======
        serializer.save(author=user_data[0])
        data = serializer.data
        data["message"] = "Article created successfully."
>>>>>>> feat(Articles): Users can can create articles
