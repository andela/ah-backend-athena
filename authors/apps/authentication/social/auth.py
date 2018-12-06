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
        
        try:
            # google_user_info = id_token.verify_oauth2_token(auth_token, requests.Request(), "341988301600-odl0nb10vaim96gsdhpa6vun7iog5pl0.apps.googleusercontent.com")
            google_user_info = id_token.verify_oauth2_token(auth_token, requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))
            google_user = google_user_info
            print("######### GOOGLE_USER: ", google_user)
            # print("####################### SUB value: ", google_user['sub'])

        except ValueError:
            google_user=None
        return google_user
    