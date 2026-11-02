# flake8: noqa

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse, RedirectResponse

from app.dependencies import get_url_shortener_service
from app.schemas.url import UrlRequest, UrlResponse
from app.services.url_shortener_service import UrlShortenerService

router = APIRouter(tags=["URL Manager"])


@router.post("/api/v1/urls", response_model=UrlResponse, status_code=status.HTTP_200_OK)
def shorten_url(
    request: UrlRequest,
    url_service: Annotated[UrlShortenerService, Depends(get_url_shortener_service)],
):
    short_url = url_service.shorten_url(request)
    return UrlResponse(short_url=short_url)


@router.get(
    "/{url_code}",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    response_class=RedirectResponse,
    responses={
        307: {
            "description": "Redirects successfully to the target long URL.",
            "headers": {
                "Location": {
                    "description": "The destination long URL.",
                    "schema": {"type": "string"},
                }
            },
        },
        200: {
            "description": "Returned when requested via Swagger UI to prevent CORS fetch errors.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "redirect_to": "https://example.com",
                    }
                }
            },
        },
    },
)
def redirect_to_long_url(
    url_code: str,
    request: Request,
    url_service: Annotated[UrlShortenerService, Depends(get_url_shortener_service)],
):
    long_url = url_service.get_long_url_from_code(url_code)

    # Detect if the request is coming from the Swagger UI docs page
    # (Checking the 'referer' header or checking if a custom test flag is passed)
    referer = request.headers.get("referer", "")

    if "/docs" in referer or "/redoc" in referer:
        # Swagger users see a clean green 200 OK with the final destination!
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "message": "Redirect intercepted for SwaggerUI or Redoc compatibility.",
                "redirect_to": long_url,
            },
        )

    return RedirectResponse(url=long_url)
