from typing import Annotated

import redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_redis_url, AsyncSessionLocal
from app.core.uow import SqlAlchemyUnitOfWork
from app.repositories.interfaces import UrlCacheRepository, UserRepository
from app.repositories.redis_url_cache_repo import RedisUrlCacheRepo
from app.repositories.user_repo import SqlAlchemyUserRepo
from app.services.url_shortener_service import UrlShortenerService
from app.services.user_service import UserService


def get_redis_client():
    client = redis.Redis.from_url(get_redis_url(), decode_responses=True)

    try:
        yield client
    finally:
        client.close()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def get_unit_of_work(session: AsyncSession = Depends(get_db)):
    return SqlAlchemyUnitOfWork(session)


def get_url_cache_repository(
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)],
) -> UrlCacheRepository:
    return RedisUrlCacheRepo(redis_client)


def get_url_shortener_service(
    url_cache_repo: Annotated[UrlCacheRepository, Depends(get_url_cache_repository)],
) -> UrlShortenerService:
    return UrlShortenerService(repo=url_cache_repo)


# Users
def get_user_repo(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return SqlAlchemyUserRepo(session)


def get_user_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work),
) -> UserService:
    return UserService(uow)
