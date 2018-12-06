import os
from google.oauth2 import id_token
from google.auth.transport import requests

class GoogleSocialAuth:
    """
    This class handles decoding of google token
    to retrieve user essentials
    """
    @staticmethod
    def validate_google_token(auth_token):
        """
            This method verifies that the provided token is valid. 
            It does this by pinging google using the 'google_oauth' library via an inbuilt method
            i.e. id_token.verify_oauth2_token.

            auth_token is encoded with user data from google
            request is what id_token will use to ping google so it can verify the token
            audience/CLIENT ID is the app on google that this token is intended for
        """
        res = {}

        try:
           google_user_info = id_token.verify_oauth2_token(auth_token, requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))
           res['google_user_info'] = google_user_info
        except ValueError:
            """auth_token is invalid"""
            res['error'] = "The token is invalid or has expired"
        
        return res
    