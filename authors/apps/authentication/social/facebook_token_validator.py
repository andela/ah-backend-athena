import facebook


class FacebookValidate:
    """
    This class contains a method that handles both the verifications and decoding
    of the facebook access_token and returns decoded user data
    """
    @staticmethod
    def validate_facebook_token(token):
        """
        This method uses the graph api (when passed an access_token) from the facebook
        sdk to call for ask for user data
        """
        try:
            graph = facebook.GraphAPI(access_token=token, version="3.1")

            user_data_from_fb = graph.request(
                '/me?fields=id,name,email,picture')

        except:
            user_data_from_fb = None
        return user_data_from_fb
