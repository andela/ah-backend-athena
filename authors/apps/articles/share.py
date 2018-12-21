"""
This module contains methods that help us share article
links via facebook, twitter, and email
"""
import os
import twitter
from ..authentication.social.twitter_token_validator import TwitterValidate, twitter
from .exceptions import InvalidAccessToken, TwitterExceptionRaised


class ShareArticle:
    """
    This class contains a static method for sharing articles to twitter
    """

    @staticmethod
    def share_via_twitter(tokens, article_url):
        """
        This method makes a post to a given twitter account
        (related to the tokens supplied)
        """
        if TwitterValidate.validate_twitter_token(tokens):
            access_token_key, access_token_secret = TwitterValidate.extract_tokens(
                tokens)
            consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
            consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
            api = twitter.Api(
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token_key=access_token_key,
                access_token_secret=access_token_secret
            )
            try:
                status = api.PostUpdate(
                    "Hi guys, check out this article on Author's Haven. {}".format(article_url))
                return status.__dict__.get('text')
            except twitter.error.TwitterError as error:
                TwitterExceptionRaised.problem_occured(error)
                raise TwitterExceptionRaised
        else:
            raise InvalidAccessToken
