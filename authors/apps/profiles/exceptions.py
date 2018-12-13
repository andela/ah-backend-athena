from rest_framework.exceptions import APIException


class ProfileDoesNotExist(APIException):
    status_code = 400
    default_detail = 'Profile does not exist.'


class UserDoesNotExist(APIException):
    status_code = 404
    default_detail = 'User does not exist'


class FollowDoesNotExist(APIException):
    status_code = 202
    default_detail = 'You are not following this user.'

    @staticmethod
    def not_following_user(username):
        status_code = 202
        default_detail = 'You are not following {}.'.format(username)
        return status_code, default_detail


class FollowingAlreadyException(APIException):
    status_code = 409
    default_detail = 'You are already following this user.'


class FollowSelfException(APIException):
    status_code = 400
    default_detail = 'You can not follow yourself.'


class NoFollowersException(APIException):
    status_code = 200
    default_detail = 'You do not have any followers.'


class NoFollowingException(APIException):
    status_code = 200
    default_detail = 'You are not following any users yet.'


class NotFollowingAnyUserException(APIException):
    status_code = 200
    default_detail = 'You are not following any user.'
