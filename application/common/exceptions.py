import dataclasses
import traceback
import typing

from .status import HttpStatusCode


def _stacktrace():
    return traceback.format_exc()


@dataclasses.dataclass
class APIExceptionJson:
    message: str
    payload: str
    stacktrace: str
    status_code: int


def make_error_message(e: Exception) -> APIExceptionJson:

    return APIExceptionJson(
        message=str(e),
        payload="",
        stacktrace=_stacktrace(),
        status_code=HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class APIException(Exception):
    message = ""
    payload: typing.Optional[typing.Union[str, dict]] = None
    status_code = HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        message: str = "",
        status_code: int = HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
        payload=None,
    ):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    @property
    def stacktrace(self):
        return _stacktrace()

    def __str__(self):
        return f"{self.message}"

    @property
    def __dict__(self):
        return {
            "payload": self.payload,
            "message": self.message,
            "stacktrace": self.stacktrace,
            "status_code": self.status_code,
        }


class InvalidAPIUsage(APIException):
    status_code = HttpStatusCode.HTTP_400_BAD_REQUEST


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
