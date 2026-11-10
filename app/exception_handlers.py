from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions import InvalidUrlException


async def invalid_url_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "code": "BAD_REQUEST", "message": str(exc)},
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(InvalidUrlException, invalid_url_handler)
