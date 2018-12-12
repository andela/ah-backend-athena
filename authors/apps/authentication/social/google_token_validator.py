import os
from google.oauth2 import id_token
from google.auth.transport import requests

class GoogleValidate:
    """
    This class contains a method that handles both the verifications and decoding
    of the google id_token and returns decoded user data
    """
    @staticmethod
    def validate_google_token(auth_token):
        """
            - This method verifies that the provided token is valid. 
            - It does this by pinging google using the 'google_oauth' library via an inbuilt method
            i.e. id_token.verify_oauth2_token.
            - auth_token is encoded with user data from google
            - request.Request() is used to connect to the google Auth Server
            - audience/CLIENT ID is the app on google console that this token is intended for
        """
        
        try:
            decoded_google_user_info = id_token.verify_oauth2_token(auth_token, requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))
        except ValueError:
            decoded_google_user_info=None
        return decoded_google_user_info