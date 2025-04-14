class DomainException(Exception):
    pass


class GroupNotFoundException(DomainException):
    pass


class DuplicateMessageException(DomainException):
    pass


class UserNotFoundException(DomainException):
    pass


class ChatNotFoundException(DomainException):
    pass
