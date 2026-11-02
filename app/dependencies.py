from typing import Annotated

import redis
from fastapi import Depends

from app.core.database import get_redis_url
from app.services.url_shortener_service import UrlShortenerService


def get_redis_client():
    client = redis.Redis.from_url(get_redis_url(), decode_responses=True)

    try:
        yield client
    finally:
        client.close()


def get_url_shortener_service(
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)],
) -> UrlShortenerService:
    return UrlShortenerService(redis_client)
