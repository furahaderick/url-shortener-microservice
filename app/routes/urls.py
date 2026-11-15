from uuid import UUID
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse

from app.dependencies import get_short_url_service
from app.schemas.short_url import ShortUrlCreate, ShortUrlResponse, ShortUrlUpdate
from app.services.short_url_service import ShortUrlService

router = APIRouter(tags=["URL Management"])


@router.get("/{short_code}")
async def redirect(
    short_code: str,
    request: Request,
    service: ShortUrlService = Depends(get_short_url_service),
):
    original_url = await service.redirect_to_long_url(short_code)

    # Detect requests coming from Swagger UI or ReDoc
    referer = request.headers.get("referer", "")

    if "/docs" in referer or "/redoc" in referer:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "message": "Redirect intercepted for SwaggerUI or Redoc compatibility.",
                "redirect_to": original_url,
            },
        )

    # Normal browser redirect
    return RedirectResponse(
        url=original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )


@router.post(
    "/api/v1/urls", response_model=ShortUrlResponse, status_code=status.HTTP_201_CREATED
)
async def create_new_url(
    url: ShortUrlCreate,
    response: Response,
    service: ShortUrlService = Depends(get_short_url_service),
):
    new_url, is_existing = await service.create_new_url(url)

    if is_existing:
        response.status_code = status.HTTP_200_OK
        response.headers["Idempotent-Replayed"] = "true"
    else:
        response.headers["Location"] = f"/{new_url.short_code}"

    return new_url


@router.get("/api/v1/urls", response_model=list[ShortUrlResponse])
async def list_user_urls(
    user_id: UUID, service: ShortUrlService = Depends(get_short_url_service)
):
    return await service.list_user_urls(user_id)


@router.get("/api/v1/urls/{short_code}", response_model=ShortUrlResponse)
async def retrieve_url_details(
    short_code: str, service: ShortUrlService = Depends(get_short_url_service)
):
    return await service.get_url_details(short_code)


@router.put("/api/v1/urls/{short_code}", response_model=ShortUrlResponse)
async def update_url(
    short_code: str,
    url: ShortUrlUpdate,
    service: ShortUrlService = Depends(get_short_url_service),
):
    return await service.update_url(short_code, url)


@router.delete("/api/v1/urls/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_url(
    short_code: str, service: ShortUrlService = Depends(get_short_url_service)
):
    await service.deactivate_url(short_code)
