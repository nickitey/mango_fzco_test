from typing import Any

from fastapi import status
from fastapi.exceptions import HTTPException


class DomainException(HTTPException):
    default_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Произошла некая ошибка"

    def __init__(
        self,
        detail: Any | None = None,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        status_code = status_code or self.default_status_code
        detail = detail or self.default_detail
        super().__init__(status_code, detail, headers)


class GroupNotFoundException(DomainException):
    pass


class DuplicateMessageException(DomainException):
    pass


class UserNotFoundException(DomainException):
    pass


class UserNotUniqueException(DomainException):
    pass


class ChatNotFoundException(DomainException):
    pass


class MessageNotFoundException(DomainException):
    pass


class TooMuchUsersForPrivateChatException(DomainException):
    pass
