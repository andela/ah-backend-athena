from rest_framework.renderers import JSONRenderer
import json


class ProfileJSONRenderer(JSONRenderer):
    """
    Checks for rendering errors if the view throws them and lets default JSONRenderer handle them
    """
    charset = 'utf-8'
    object_label = 'profile'

    def render(self, data, media_type=None, renderer_context=None):
        errors = data.get('errors', None)

        if errors is not None:
            return super(ProfileJSONRenderer, self).render(data)
        return json.dumps({
            self.object_label: data
        })
