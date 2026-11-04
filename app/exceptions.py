class AppException(Exception):
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class InvalidUrlException(AppException):
    def __init__(self, message: str = "Invalid URL", error_code: str = "BAD_REQUEST"):
        super().__init__(message, error_code)
