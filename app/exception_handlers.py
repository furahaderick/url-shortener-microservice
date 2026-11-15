from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions import (
    InvalidUrlException,
    UrlExpiredException,
    UrlInactiveException,
    UrlNotFoundException,
    UserAlreadyExistsException,
    UserNotFoundException,
)


async def invalid_url_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "code": "BAD_REQUEST", "message": str(exc)},
    )


async def user_already_exists_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "code": "BAD_REQUEST", "message": str(exc)},
    )


async def user_not_found_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"success": False, "code": "NOT_FOUND", "message": str(exc)},
    )


async def url_not_found_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"success": False, "code": "NOT_FOUND", "message": str(exc)},
    )


async def url_inactive_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"success": False, "code": "FORBIDDEN", "message": str(exc)},
    )


async def url_expired_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_410_GONE,
        content={"success": False, "code": "GONE", "message": str(exc)},
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(InvalidUrlException, invalid_url_handler)
    app.add_exception_handler(UserAlreadyExistsException, user_already_exists_handler)
    app.add_exception_handler(UserNotFoundException, user_not_found_handler)
    app.add_exception_handler(UrlNotFoundException, url_not_found_handler)
    app.add_exception_handler(UrlInactiveException, url_inactive_handler)
    app.add_exception_handler(UrlExpiredException, url_expired_handler)
