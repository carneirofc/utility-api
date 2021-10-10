import traceback

from .status import HttpStatusCode


def _stracktrace():
    return traceback.format_exc()


class APIException(Exception):
    status_code = HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR
    message = ""

    def __init__(self, message=None):
        if message is not None:
            self.message = message

    def to_dict(self):
        return {
            "message": self.message,
            "stacktrace": self.stacktrace,
            "status_code": self.status_code,
        }

    @property
    def stacktrace(self):
        return _stracktrace()

    def __str__(self):
        return f"{self}(message={self.message})"


class ParseError(APIException):
    status_code = HttpStatusCode.HTTP_400_BAD_REQUEST
    message = "Malformed request."


class AuthenticationFailed(APIException):
    status_code = HttpStatusCode.HTTP_401_UNAUTHORIZED
    message = "Incorrect authentication credentials."


class NotAuthenticated(APIException):
    status_code = HttpStatusCode.HTTP_401_UNAUTHORIZED
    message = "Authentication credentials were not provided."


class PermissionDenied(APIException):
    status_code = HttpStatusCode.HTTP_403_FORBIDDEN
    message = "You do not have permission to perform this action."


class NotFound(APIException):
    status_code = HttpStatusCode.HTTP_404_NOT_FOUND
    message = "This resource does not exist."


class NotAcceptable(APIException):
    status_code = HttpStatusCode.HTTP_406_NOT_ACCEPTABLE
    message = "Could not satisfy the request Accept header."


class UnsupportedMediaType(APIException):
    status_code = HttpStatusCode.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    message = "Unsupported media type in the request Content-Type header."


class Throttled(APIException):
    status_code = HttpStatusCode.HTTP_429_TOO_MANY_REQUESTS
    message = "Request was throttled."
