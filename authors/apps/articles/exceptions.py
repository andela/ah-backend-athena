"""
Write customized exception classes here
"""
from rest_framework.exceptions import APIException


class PermisionDenied(APIException):
    status_code = 403
    default_detail = 'You dont have permission to perform this action'

class CommentDoesNotExist(APIException):
    status_code = 404
    default_detail = "Failed, comment or article doesnot exist"