import logging
from datetime import UTC, datetime
from uuid import UUID

from redis.exceptions import RedisError
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    AliasAlreadyExistsException,
    InsufficientPermissionsException,
    UrlExpiredException,
    UrlInactiveException,
    UrlNotFoundException,
)
from app.core.tier_entitlements import TierEntitlements
from app.core.uow import SqlAlchemyUnitOfWork
from app.core.utils import generate_unique_code
from app.models.click import Click
from app.models.short_url import ShortUrl
from app.models.user import User
from app.schemas.short_url import ShortUrlCreate, ShortUrlUpdate
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class ShortUrlService:
    def __init__(self, uow: SqlAlchemyUnitOfWork, cache_service: CacheService):
        self.uow = uow
        self.cache = cache_service

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
    async def create_new_url(
        self,
        entitlements: TierEntitlements,
        user: User,
        url: ShortUrlCreate,
        max_retries: int = 5,
    ):

        # Check non-db tier entitlements
        if url.custom_alias is not None and not entitlements.allow_custom_aliases:
            raise InsufficientPermissionsException(
                message="Custom aliases are only available on Premium tiers."
            )

        async with self.uow:
            # Lock user row to handle concurrent requests that create a url
            await self.uow.users.lock_user_row(user.id)

            # Check if long url already exists
            original_url = str(url.original_url)
            existing_url = await self.uow.urls.find_by_original_url_and_user_id(
                original_url, user.id
            )
            if existing_url is not None:
                return existing_url, True

            # Check maximum active urls limit
            if entitlements.max_active_urls is not None:
                active_count = await self.uow.urls.count_active_urls_by_user_id(user.id)
                if active_count >= entitlements.max_active_urls:
                    raise InsufficientPermissionsException(
                        message=(
                            "You have reached your limit of "
                            f"{entitlements.max_active_urls} active URLs. "
                            "Upgrade to Premium for unlimited URLs."
                        )
                    )

            url_data = url.model_dump(exclude={"original_url"})

            # Check if custom alias is already taken
            if url.custom_alias is not None:
                existing_alias = await self.uow.urls.get_url_by_alias(url.custom_alias)
                if existing_alias is not None:
                    raise AliasAlreadyExistsException()

            # Enter the short_code generation retry loop
            for attempt in range(max_retries):
                # Use an isolated async savepoint to avoid losing session state
                try:
                    async with self.uow.session.begin_nested():
                        # Generate a fresh unique string code
                        code = generate_unique_code()

                        # Create db url with original url and short code
                        db_url = ShortUrl(
                            owner_id=user.id,
                            original_url=original_url,
                            short_code=code,
                            **url_data,
                        )

                        new_url = await self.uow.urls.add_url(db_url)

                    # Commit if successfully
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
            return await self.uow.urls.get_user_urls(user_id)

    async def get_url_details(self, short_code: str, user_id: UUID):
        async with self.uow:
            url = await self.uow.urls.get_url_by_short_code_and_user_id(
                short_code, user_id
            )
            if url is None:
                raise UrlNotFoundException()

            return url

    async def update_url(
        self,
        entitlements: TierEntitlements,
        short_code: str,
        url: ShortUrlUpdate,
        user_id: UUID,
    ):
        # Check non-db tier entitlements
        if url.custom_alias is not None and not entitlements.allow_custom_aliases:
            raise InsufficientPermissionsException(
                message="Custom aliases are only available on Premium tiers."
            )

        async with self.uow:
            existing_url = await self.uow.urls.get_url_by_short_code_and_user_id(
                short_code, user_id
            )
            if existing_url is None:
                raise UrlNotFoundException()

            update_data = url.model_dump(exclude_unset=True)
            updated_url = await self.uow.urls.update_url(existing_url, update_data)

            # Commit
            await self.uow.commit()

            return updated_url

    async def deactivate_url(self, short_code: str, user_id: UUID):
        async with self.uow:
            existing_url = await self.uow.urls.get_url_by_short_code_and_user_id(
                short_code, user_id
            )
            if existing_url is None:
                raise UrlNotFoundException()

            existing_url.is_active = False

            # Commit
            await self.uow.commit()

            # Invalidate redis cache after successful deactivation
            try:
                await self.cache.delete(f"url:{short_code}")
            except RedisError:
                logger.warning(
                    "Failed to invalidate cache for short URL: %s",
                    short_code,
                )

            # Optional return
            return existing_url

    async def redirect_to_long_url(
        self,
        short_code: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        referrer: str | None = None,
        city: str | None = None,
        country: str | None = None,
    ):
        cache_key = f"url:{short_code}"
        cached_url = None

        # 1. Try Redis first
        try:
            cached_url = await self.cache.get(cache_key)

        except (RedisError, ValueError):
            logger.warning(
                "Redis lookup failed for %s",
                short_code,
            )

        cache_data = None

        async with self.uow:
            # 2. Cache miss: retrieve metadata from PostgreSQL
            if cached_url is None:
                existing_url = await self.uow.urls.get_url_by_short_code(short_code)

                if existing_url is None:
                    raise UrlNotFoundException()

                url_id = existing_url.id
                original_url = str(existing_url.original_url)
                is_active = existing_url.is_active
                expires_at = existing_url.expires_at

                cache_data = {
                    "id": url_id,
                    "original_url": original_url,
                    "is_active": is_active,
                    "expires_at": (expires_at.isoformat() if expires_at else None),
                }

            # 3. Cache hit: retrieve cached metadata
            else:
                url_id = cached_url["id"]
                original_url = cached_url["original_url"]
                is_active = cached_url["is_active"]

                expires_at = (
                    datetime.fromisoformat(cached_url["expires_at"])
                    if cached_url["expires_at"]
                    else None
                )

            # 4. Validate URL
            if not is_active:
                raise UrlInactiveException()

            if expires_at is not None and expires_at <= datetime.now(UTC):
                raise UrlExpiredException()

            # 5. Record click
            click = Click(
                short_url_id=url_id,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer,
                city=city,
                country=country,
            )

            await self.uow.clicks.add_click(click)

            # 6. Increment click count atomically & Commit
            await self.uow.session.execute(
                update(ShortUrl)
                .where(ShortUrl.id == url_id)
                .values(click_count=ShortUrl.click_count + 1)
            )

            await self.uow.commit()

        # 7. Populate Redis after successful database transaction
        if cache_data is not None:
            ttl = 3600

            if expires_at is not None:
                remaining = int((expires_at - datetime.now(UTC)).total_seconds())
                ttl = min(ttl, remaining)

            if ttl > 0:
                try:
                    await self.cache.set(
                        cache_key,
                        cache_data,
                        ttl=ttl,
                    )

                except (RedisError, TypeError):
                    logger.warning(
                        "Redis write failed for %s",
                        short_code,
                    )

        return original_url
