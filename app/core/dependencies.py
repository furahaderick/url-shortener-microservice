from typing import Annotated
from uuid import UUID

import redis
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_redis_url
from app.core.exceptions import InsufficientPermissionsException, InvalidTokenException
from app.core.security import TokenType, decode_token
from app.core.uow import SqlAlchemyUnitOfWork
from app.models.user import User, UserTier
from app.services.analytics_service import AnalyticsService
from app.services.short_url_service import ShortUrlService
from app.services.user_service import UserService

# auto_error=True -> FastAPI returns 401 by default if auth header is missing
bearer_scheme = HTTPBearer(auto_error=True)


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


# UOW
def get_unit_of_work(session: AsyncSessionDep):
    return SqlAlchemyUnitOfWork(session)


UOWDep = Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)]


# Auth
BearerCredentials = Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]


async def get_current_user(credentials: BearerCredentials, uow: UOWDep) -> User:
    token = credentials.credentials

    async with uow:
        try:
            payload = decode_token(token=token)

            if payload.get("type") != TokenType.ACCESS:
                raise InvalidTokenException()

            user_uuid = UUID(payload["sub"])

        except (PyJWTError, KeyError, ValueError, TypeError):
            raise InvalidTokenException()

        user = await uow.users.get_user_by_id(user_uuid)

        if user is None:
            raise InvalidTokenException()

        return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def require_tiers(*allowed_tiers: UserTier):
    def _checker(current_user: CurrentUserDep) -> User:
        if current_user.tier not in allowed_tiers:
            raise InsufficientPermissionsException(
                message=(
                    f"Requires one of the following tiers: {', '.join(allowed_tiers)}"
                )
            )
        return current_user

    return _checker


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


# Analytics
def get_analytics_service(uow: UOWDep) -> AnalyticsService:
    return AnalyticsService(uow)


AnalyticsServiceDep = Annotated[AnalyticsService, Depends(get_analytics_service)]
