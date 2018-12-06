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
        if header:
            token = header.split()[1].decode('utf-8')
            return token
        return None

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
            payload = jwt.decode(user_token, settings.SECRET_KEY)
        except jwt.ExpiredSignatureError:
            expired_error = 'Token expired. Please log in again.'
            raise exceptions.AuthenticationFailed(expired_error)
        except jwt.InvalidTokenError:
            invalid_error = 'Invalid token. please login again'
            raise exceptions.AuthenticationFailed(invalid_error)
        try:
            user = User.objects.get(id=payload['id'])
        except (user.DoesNotExist, user.PasswordDoesNotMacth):
            error = 'Invalid user credentials'
            raise exceptions.AuthenticationFailed(error)
        return (user, user_token)
