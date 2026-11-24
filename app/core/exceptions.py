class AppException(Exception):
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class InvalidUrlException(AppException):
    def __init__(self, message: str = "Invalid URL", error_code: str = "BAD_REQUEST"):
        super().__init__(message, error_code)


class UserAlreadyExistsException(AppException):
    def __init__(
        self,
        message: str = "A user with this email already exists.",
        error_code: str = "USER_ALREADY_EXISTS",
    ):
        super().__init__(message, error_code)


class UserNotFoundException(AppException):
    def __init__(
        self, message: str = "User not found", error_code: str = "USER_NOT_FOUND"
    ):
        super().__init__(message, error_code)


class UrlNotFoundException(AppException):
    def __init__(
        self, message: str = "URL not found", error_code: str = "URL_NOT_FOUND"
    ):
        super().__init__(message, error_code)


class UrlInactiveException(AppException):
    def __init__(
        self, message: str = "URL is inactive", error_code: str = "URL_INACTIVE"
    ):
        super().__init__(message, error_code)


class UrlExpiredException(AppException):
    def __init__(
        self, message: str = "URL has expired", error_code: str = "URL_EXPIRED"
    ):
        super().__init__(message, error_code)


class InvalidCredentialsException(AppException):
    def __init__(
        self,
        message: str = "Wrong email or password",
        error_code: str = "INVALID_CREDENTIALS",
    ):
        super().__init__(message, error_code)


class InvalidTokenException(AppException):
    def __init__(
        self,
        message: str = "Invalid or Expired token",
        error_code: str = "INVALID_TOKEN",
    ):
        super().__init__(message, error_code)


class InsufficientPermissionsException(AppException):
    def __init__(
        self,
        message: str = "Insufficient permissions",
        error_code: str = "INSUFFICIENT_PERMISSIONS",
    ):
        super().__init__(message, error_code)


class InvalidRedirectException(AppException):
    def __init__(
        self,
        message: str = "Invalid redirect destination.",
        error_code: str = "INVALID_REDIRECT",
    ):
        super().__init__(message, error_code)


class AliasAlreadyExistsException(AppException):
    def __init__(
        self,
        message: str = "Custom alias name is already taken.",
        error_code: str = "ALIAS_ALREADY_EXISTS",
    ):
        super().__init__(message, error_code)
