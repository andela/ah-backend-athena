import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import User

"""Configure JWT Here"""


class JWTAuthentication:
    """
    This class implements a custom authentication by overriding
    the .authenticate(self, request) method. The method returns
    a two-tuple of (user, token) on successfull authentication
    and None  otherwise.
    """

    def authenticate_header(self, request):
        """
        This method returns 'None' if authentication is not attempted
        Otherwise it returns the token.
        """
        header = authentication.get_authorization_header(request)
        token = None
        try:
            token = header.split()[1].decode('utf-8')
        except:
            raise exceptions.AuthenticationFailed(
                'Token not found in the header')
        finally:
            return token

    def authenticate(self, request):
        """
        This method gets the token from the authenticate_header method
        and perform permission checks on the token. When the checks
        fails, a AuthenticationFailed exception is raised otherwise
        a user object and token are returned.
        """
        user_token = self.authenticate_header(request)
        if not user_token:
            return None
        try:
            payload_id = self.decode_token(user_token)
            user = User.objects.get(id=payload_id)
        except (User.DoesNotExist):
            raise exceptions.AuthenticationFailed('Invalid user credentials')
        return (user, user_token)

    def decode_token(self, user_token):
        try:
            payload = jwt.decode(user_token, settings.SECRET_KEY)
            return payload['id']
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed(
                'Invalid token. please login again')
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                'Token expired. Please log in again.')
