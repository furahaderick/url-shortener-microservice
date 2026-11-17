from typing import Annotated

import redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_redis_url
from app.core.uow import SqlAlchemyUnitOfWork
from app.services.short_url_service import ShortUrlService
from app.services.user_service import UserService


def get_redis_client():
    client = redis.Redis.from_url(get_redis_url(), decode_responses=True)

    try:
        yield client
    finally:
        client.close()


RedisDep = Annotated[redis.Redis, Depends(get_redis_client)]


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_unit_of_work(session: AsyncSessionDep):
    return SqlAlchemyUnitOfWork(session)


UOWDep = Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)]


# Users
def get_user_service(
    uow: UOWDep,
) -> UserService:
    return UserService(uow)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


# Short URLs
def get_short_url_service(
    uow: UOWDep,
) -> ShortUrlService:
    return ShortUrlService(uow)


ShortUrlServiceDep = Annotated[ShortUrlService, Depends(get_short_url_service)]
