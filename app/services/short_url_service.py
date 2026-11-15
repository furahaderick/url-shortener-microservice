from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import update
from app.core.uow import SqlAlchemyUnitOfWork
from app.exceptions import (
    UrlExpiredException,
    UrlInactiveException,
    UrlNotFoundException,
    UserNotFoundException,
)
from app.models.short_url import ShortUrl
from app.schemas.short_url import ShortUrlCreate, ShortUrlUpdate


class ShortUrlService:
    def __init__(self, uow: SqlAlchemyUnitOfWork):
        self.uow = uow

    async def get_active_urls(self):
        async with self.uow:
            active_urls = await self.uow.urls.active_urls()
            return active_urls

    async def get_expired_urls(self):
        async with self.uow:
            expired_urls = await self.uow.urls.expired_urls()
            return expired_urls

    async def get_popular_urls(self):
        async with self.uow:
            popular_urls = await self.uow.urls.popular_urls()
            return popular_urls

    async def create_new_url(self, url: ShortUrlCreate):
        async with self.uow:

            # Check if user exists
            existing_user = await self.uow.users.get_user_by_id(url.owner_id)

            if existing_user is None:
                raise UserNotFoundException()

            # Check if long url already exists
            original_url = str(url.original_url)
            existing_url = await self.uow.urls.find_by_original_url(original_url)

            if existing_url is not None:
                return existing_url

            # unique_code is generated automatically by default
            new_url = await self.uow.urls.add_url(url)

            # Commit
            await self.uow.commit()

            return new_url

    async def list_user_urls(self, user_id: UUID):
        async with self.uow:
            # Check if user exists
            existing_user = await self.uow.users.get_user_by_id(user_id)

            if existing_user is None:
                raise UserNotFoundException()

            return await self.uow.urls.get_user_urls(user_id)

    async def get_url_details(self, short_code: str):
        async with self.uow:
            # TODO: Perform ownership check
            url = await self.uow.urls.get_url_by_short_code(short_code)
            if url is None:
                raise UrlNotFoundException()

            return url

    async def update_url(self, short_code: str, url: ShortUrlUpdate):
        async with self.uow:
            # TODO: Perform ownership check
            existing_url = await self.uow.urls.get_url_by_short_code(short_code)
            if existing_url is None:
                raise UrlNotFoundException()

            update_data = url.model_dump(exclude_unset=True)
            updated_url = await self.uow.urls.update_url(existing_url, update_data)

            # Commit
            await self.uow.commit()

            return updated_url

    async def deactivate_url(self, short_code: str):
        async with self.uow:
            # TODO: Perform ownership check
            existing_url = await self.uow.urls.get_url_by_short_code(short_code)
            if existing_url is None:
                raise UrlNotFoundException()

            existing_url.is_active = False

            # Commit
            await self.uow.commit()

            # Optional return
            return existing_url

    async def redirect_to_long_url(self, short_code: str):
        async with self.uow:
            existing_url = await self.uow.urls.get_url_by_short_code(short_code)
            if existing_url is None:
                raise UrlNotFoundException()

            if not existing_url.is_active:
                raise UrlInactiveException()

            if (
                existing_url.expires_at is not None
                and existing_url.expires_at <= datetime.now(timezone.utc)
            ):
                raise UrlExpiredException()

            await self.uow.session.execute(
                update(ShortUrl)
                .where(ShortUrl.id == existing_url.id)
                .values(click_count=ShortUrl.click_count + 1)
            )

            # Commit
            await self.uow.commit()

            return str(existing_url.original_url)
