from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from app.models.click import Click
from app.models.short_url import ShortUrl
from app.models.user import User


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

    @abstractmethod
    async def find_by_original_url_and_user_id(
        self, original_url: str, user_id: UUID
    ) -> ShortUrl | None:
        """Returns a url queried by its original, long url"""

    @abstractmethod
    async def add_url(self, url: ShortUrl) -> ShortUrl:
        """Returns a newly created url"""

    @abstractmethod
    async def get_user_urls(self, user_id: UUID) -> Sequence[ShortUrl]:
        """Returns urls queried by user id"""

    @abstractmethod
    async def get_url_by_short_code_and_user_id(
        self, short_code: str, user_id: UUID
    ) -> ShortUrl | None:
        """Returns an active url queried by its id and user id"""

    @abstractmethod
    async def get_url_by_short_code(self, short_code: str) -> ShortUrl | None:
        """Returns a url queried by its id"""

    @abstractmethod
    async def update_url(self, url: ShortUrl, url_data: dict) -> ShortUrl:
        """Updates a url"""

    @abstractmethod
    async def count_active_urls_by_user_id(self, user_id: UUID) -> int:
        """Counts all active urls owned by a user with user_id"""

    @abstractmethod
    async def get_url_by_alias(self, custom_alias: str) -> ShortUrl | None:
        """Returns a url queried by its custom alias"""


class UserRepository(ABC):
    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        """Returns a user queried by email"""

    @abstractmethod
    async def add_user(self, user: User) -> User:
        """Returns a newly created user"""

    @abstractmethod
    async def lock_user_row(self, user_id: UUID) -> None:
        """Locks a user row with user_id"""

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Returns a user queried by user id"""


class ClickRepository(ABC):
    @abstractmethod
    async def add_click(self, click: Click) -> None:
        """Returns a newly created click"""

    @abstractmethod
    async def get_url_click_analytics(self, url_id: UUID):
        """
        Returns click analytics
        (total clicks & time series)
        for a url queried by its id
        """
