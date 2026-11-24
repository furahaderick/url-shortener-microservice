from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse

from app.core.dependencies import CurrentUserDep, ShortUrlServiceDep, require_tiers
from app.core.exceptions import InvalidRedirectException
from app.models.user import UserTier
from app.schemas.short_url import (
    ShortUrlCreate,
    ShortUrlResponse,
    ShortUrlUpdate,
    ShortUrlWithOwnerResponse,
)

router = APIRouter(tags=["URL Management"])


@router.get("/{short_code}")
async def redirect(
    short_code: str,
    request: Request,
    service: ShortUrlServiceDep,
):
    ip_address = request.client.host if request.client else None
    # Truncate user_agent to respect database limit
    user_agent = request.headers.get("user-agent", "Unknown")[:100]
    referrer = request.headers.get("referer")

    original_url = await service.redirect_to_long_url(
        short_code=short_code,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer,
    )

    # Ensure redirect uses http or https for security
    parsed_url = urlsplit(original_url)

    if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
        raise InvalidRedirectException()

    # Detect requests coming from Swagger UI or ReDoc
    if referrer and any(path in referrer for path in ("/docs", "/redoc")):
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


@router.get(
    "/api/v1/urls/active",
    response_model=list[ShortUrlWithOwnerResponse],
    dependencies=[Depends(require_tiers(UserTier.ADMIN))],
)
async def get_active_urls(service: ShortUrlServiceDep):
    return await service.get_active_urls()


@router.get(
    "/api/v1/urls/expired",
    response_model=list[ShortUrlWithOwnerResponse],
    dependencies=[Depends(require_tiers(UserTier.ADMIN))],
)
async def get_expired_urls(service: ShortUrlServiceDep):
    return await service.get_expired_urls()


@router.get(
    "/api/v1/urls/popular",
    response_model=list[ShortUrlWithOwnerResponse],
    dependencies=[Depends(require_tiers(UserTier.ADMIN))],
)
async def get_popular_urls(service: ShortUrlServiceDep):
    return await service.get_popular_urls()


@router.post(
    "/api/v1/urls", response_model=ShortUrlResponse, status_code=status.HTTP_201_CREATED
)
async def create_new_url(
    url: ShortUrlCreate,
    response: Response,
    service: ShortUrlServiceDep,
    current_user: CurrentUserDep,
):
    new_url, is_existing = await service.create_new_url(current_user.id, url)

    if is_existing:
        response.status_code = status.HTTP_200_OK
        response.headers["Idempotent-Replayed"] = "true"
    else:
        response.headers["Location"] = f"/{new_url.short_code}"

    return new_url


@router.get("/api/v1/urls", response_model=list[ShortUrlResponse])
async def list_user_urls(service: ShortUrlServiceDep, current_user: CurrentUserDep):
    return await service.list_user_urls(current_user.id)


@router.get("/api/v1/urls/{short_code}", response_model=ShortUrlResponse)
async def retrieve_url_details(
    short_code: str, service: ShortUrlServiceDep, current_user: CurrentUserDep
):
    return await service.get_url_details(short_code, current_user.id)


@router.put("/api/v1/urls/{short_code}", response_model=ShortUrlResponse)
async def update_url(
    short_code: str,
    url: ShortUrlUpdate,
    service: ShortUrlServiceDep,
    current_user: CurrentUserDep,
):
    return await service.update_url(short_code, url, current_user.id)


@router.delete("/api/v1/urls/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_url(
    short_code: str, service: ShortUrlServiceDep, current_user: CurrentUserDep
):
    await service.deactivate_url(short_code, current_user.id)
