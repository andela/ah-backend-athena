from rest_framework.serializers import RelatedField
from django.template.defaultfilters import slugify
from .models import Tag

class TagField(RelatedField):
    """
    Override the RelatedField serializer in order to serialize tags according to a specific article
    """
    def get_queryset(self):
        return Tag.objects.all()

    def to_internal_value(self, data):
        tag, created = Tag.objects.get_or_create(
            tag=data, slug=slugify(data).replace('_', '-'))

        return tag

    def to_representation(self, value):
        return value.tag

