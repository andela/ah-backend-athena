"""
Write customized exception classes here
"""
from rest_framework.exceptions import APIException


class PermisionDenied(APIException):
    status_code = 403
    default_detail = 'You dont have permission to perform this action'


class CommentDoesNotExist(APIException):
    status_code = 404
    default_detail = "Failed, comment or article does not exist"


class MissingAccessTokenInRequestException(APIException):
    """
    exception class for a missing access token
    """
    status_code = 400
    default_detail = "Missing access_token parameter in the request body, it is required"


class MissingTwitterTokensInRequestException(APIException):
    """
    exception class for a missing tokens param
    """
    status_code = 400
    default_detail = "Missing tokens parameter in the request body, it is required"


class MissingEmailInRequestBodyException(APIException):
    """
    exception class for a missing emails
    """
    status_code = 400
    default_detail = "Missing 'send_to' (Email address to share to)" +\
        " parameter in the request body, it is required"


class InvalidEmailAddress(APIException):
    """
    exception class for a invalid email
    """
    status_code = 400
    default_detail = "The email string provided is invalid"


class FailedToSendEmailException(APIException):
    """
    exception class for a invalid email
    """
    status_code = 500
    default_detail = "Something bad happened and we were unable to send the email, try again later."

    @classmethod
    def change_error_message(cls, message):
        """
        This method changes the outputted error message 
        depending on the exception met during send mail
        """
        cls.default_detail = message


class InvalidAccessToken(APIException):
    """
    exception class for a missing access token
    """
    status_code = 400
    default_detail = "The access_token provided is invalid"


class TwitterTokenInputsFormatError(APIException):
    """
    exception class for a invalid formatting of twitter tokens
    """
    status_code = 400
    default_detail = "Invalid format supplied twitter credentials. " + \
        "Correct format is: '<access_token_key> <access_token_secret>'"


class TwitterExceptionRaised(APIException):
    """
    This class handles twitter error messages
    """
    status_code = 400
    default_detail = "Something bad happened with the twitter API"

    @classmethod
    def problem_occured(cls, message):
        """
        This method returns a dynamic error message passed in from
        the TwitterError that occured
        """
        cls.status_code = 400
        cls.default_detail = message
