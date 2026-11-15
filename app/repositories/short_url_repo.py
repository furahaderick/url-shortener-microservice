from datetime import datetime, timezone
from typing import Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models.short_url import ShortUrl
from app.repositories.interfaces import ShortUrlRepository
from app.schemas.short_url import ShortUrlCreate


class SqlAlchemyShortUrlRepo(ShortUrlRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def active_urls(self) -> list[ShortUrl]:
        now = datetime.now(timezone.utc)

        stmt = (
            select(ShortUrl)
            .options(joinedload(ShortUrl.owner))
            .where(
                ShortUrl.is_active.is_(True),
                (ShortUrl.expires_at.is_(None)) | (ShortUrl.expires_at > now),
            )
        )

        result = await self.session.scalars(stmt)
        return list(result.all())

    async def expired_urls(self) -> list[ShortUrl]:
        now = datetime.now(timezone.utc)

        stmt = (
            select(ShortUrl)
            .options(joinedload(ShortUrl.owner))
            .where(
                ShortUrl.expires_at.is_not(None),
                ShortUrl.expires_at <= now,
            )
        )

        result = await self.session.scalars(stmt)
        return list(result.all())

    async def popular_urls(self) -> list[ShortUrl]:
        stmt = (
            select(ShortUrl)
            .options(joinedload(ShortUrl.owner))
            .order_by(ShortUrl.click_count.desc())
        )

        result = await self.session.scalars(stmt)
        return list(result.all())

    async def add_url(self, url: ShortUrlCreate):
        url_data = url.model_dump(exclude={"original_url"})
        new_url = ShortUrl(original_url=str(url.original_url), **url_data)
        self.session.add(new_url)
        await self.session.flush()
        await self.session.refresh(new_url)
        return new_url

    async def get_user_urls(self, user_id: UUID) -> Sequence[ShortUrl]:
        stmt = select(ShortUrl).where(ShortUrl.owner_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_url_by_short_code(self, short_code: str):
        stmt = select(ShortUrl).where(ShortUrl.short_code == short_code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_url(self, url: ShortUrl, url_data: dict):
        for key, value in url_data.items():
            setattr(url, key, value)

        await self.session.flush()
        return url

    async def find_by_original_url(self, original_url: str):
        stmt = select(ShortUrl).where(ShortUrl.original_url == original_url)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
