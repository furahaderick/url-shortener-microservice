from typing import Annotated

import redis
from fastapi import Depends

from app.core.database import get_redis_url
from app.repositories.interfaces import UrlCacheRepository
from app.repositories.redis_url_cache_repo import RedisUrlCacheRepo
from app.services.url_shortener_service import UrlShortenerService


def get_redis_client():
    client = redis.Redis.from_url(get_redis_url(), decode_responses=True)

    try:
        yield client
    finally:
        client.close()


def get_url_cache_repository(
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)],
) -> UrlCacheRepository:
    return RedisUrlCacheRepo(redis_client)


def get_url_shortener_service(
    url_cache_repo: Annotated[UrlCacheRepository, Depends(get_url_cache_repository)],
) -> UrlShortenerService:
    return UrlShortenerService(repo=url_cache_repo)
