from abc import ABC, abstractmethod
from typing import Sequence

from app.models.short_url import ShortUrl
from app.schemas.user import UserCreate


class UrlCacheRepository(ABC):
    @abstractmethod
    def get_code_by_url(self, url: str) -> str | None:
        pass

    @abstractmethod
    def save_url(self, code: str, url: str) -> None:
        pass

    @abstractmethod
    def get_url_by_code(self, code: str) -> str | None:
        pass


class ShortUrlRepository(ABC):
    @abstractmethod
    async def active_urls(self) -> Sequence[ShortUrl]:
        """Return URLs that are active and have not expired."""

    @abstractmethod
    async def expired_urls(self) -> Sequence[ShortUrl]:
        """Return URLs whose expiration date has passed."""

    @abstractmethod
    async def popular_urls(self) -> Sequence[ShortUrl]:
        """Return URLs ordered by click count (highest first)."""


class UserRepository(ABC):

    @abstractmethod
    async def get_user_by_email(self, email: str):
        """Returns a user queried by email"""

    @abstractmethod
    async def add_user(self, user: UserCreate):
        """Returns a newly created user"""
