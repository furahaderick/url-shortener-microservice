from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    UrlExpiredException,
    UrlInactiveException,
    UrlNotFoundException,
    UserNotFoundException,
)
from app.core.uow import SqlAlchemyUnitOfWork
from app.core.utils import generate_unique_code
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

    # Create new url with retry mechanism for duplicate short code generation
    async def create_new_url(self, url: ShortUrlCreate, max_retries: int = 5):

        async with self.uow:
            # Check if user exists
            existing_user = await self.uow.users.get_user_by_id(url.owner_id)
            if existing_user is None:
                raise UserNotFoundException()

            # Check if long url already exists
            original_url = str(url.original_url)
            existing_url = await self.uow.urls.find_by_original_url(original_url)
            if existing_url is not None:
                return existing_url, True

            url_data = url.model_dump(exclude={"original_url"})

            # Enter the short_code generation retry loop
            for attempt in range(max_retries):
                # Use an isolated async savepoint to avoid losing session state
                async with self.uow.session.begin_nested():
                    try:
                        # Generate a fresh unique string code
                        code = generate_unique_code()

                        # Create db url with original url and short code
                        db_url = ShortUrl(
                            original_url=original_url, short_code=code, **url_data
                        )

                        new_url = await self.uow.urls.add_url(db_url)

                        # Commit if successful
                        await self.uow.commit()
                        return new_url, False

                    except IntegrityError as exc:
                        # The nested context manager rolls back ONLY to the savepoint.
                        # The parent transaction remains untouched.

                        # Extract psycopg's constraint metadata
                        orig_exception = getattr(exc, "orig", None)
                        diag = getattr(orig_exception, "diag", None)
                        constraint_name = getattr(diag, "constraint_name", None)

                        # Verify the error belongs strictly to our short_code constraint
                        if constraint_name == "uq_short_urls_short_code":
                            if attempt == max_retries - 1:
                                raise  # Out of retries, raise up the final error
                            continue  # Collision caught safely. Try the loop again.

                        # Re-raise immediately if it's an unrelated constraint failure
                        raise

            raise RuntimeError(
                "Unable to generate a unique short code after maximum retries"
            )

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
                and existing_url.expires_at <= datetime.now(UTC)
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
