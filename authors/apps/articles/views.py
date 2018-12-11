
import uuid
from django.shortcuts import render
from rest_framework import status, exceptions
from rest_framework.generics import(
    RetrieveUpdateAPIView,
    GenericAPIView
)

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.template.defaultfilters import slugify

from ..authentication.backends import JWTAuthentication
from ..authentication.models import User
from .renderers import ArticleJSONRenderer
from .models import ArticleImg, Article
from ..profiles.models import Profile

from .serializers import(
    CreateArticleViewSerializer,


)


class createArticleView(GenericAPIView):
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

        image_data = article['image']

        image_obj = ArticleImg(
            image_url=image_data['image_url'],
            description=image_data['image_description']
        )
        image_obj.save()
        img_id = ArticleImg.objects.filter(
            image_url=image_data['image_url']).first()
        article['image'] = img_id.id

        """create slug from an artical"""

        slug = slugify(article['title']).replace('_', '-')
        article['slug'] = slug

        current_user = User.objects.all().filter(
            email=request.user).values()[0]
        user_id = current_user['id']
        profile = Profile.objects.get(user__id=user_id)

        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=profile)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
