import os
import twitter
import json
from dotenv import load_dotenv
load_dotenv()


class TwitterValidate:
    """
    This class contains methods that handle both the verification and
    decoding of the twitter access_token and returns decoded user data
    """

    @staticmethod
    def extract_tokens(tokens):
        auth_tokens = tokens.split(' ')
        if len(auth_tokens) < 2:
            return 'invalid token', 'invalid token'
        access_token_key = auth_tokens[0]
        access_token_secret = auth_tokens[1]

        return access_token_key, access_token_secret

    @staticmethod
    def validate_twitter_token(tokens):
        """
        Validate twitter tokens using twitter api sdk
        VerifyCredentials() returns a .twitter.User model object
        We convert it to a dictionary to make it easier to work with in other classes/methods
        """
        access_token_key, access_token_secret = TwitterValidate.extract_tokens(
            tokens)

        try:
            consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
            consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
            api = twitter.Api(
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token_key=access_token_key,
                access_token_secret=access_token_secret
            )
            
            user_data_from_twitter = api.VerifyCredentials(include_email=True)
            return user_data_from_twitter.__dict__

        except:
            return None
