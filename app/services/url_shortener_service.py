from typing import Final

import redis
from app.exceptions import InvalidUrlException

from app.core.config import settings
from app.schemas.url import UrlRequest
from app.utils import generate_unique_id


class UrlShortenerService:
    MAP_NAME: Final = "long_urls"

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def shorten_url(self, req: UrlRequest) -> tuple[str, bool]:
        # Check if the code for this url already exists
        url = str(req.url)
        existing_id_code = self.redis.hget(UrlShortenerService.MAP_NAME, url)

        if existing_id_code is not None:
            return f"{settings.APP_DOMAIN}/{existing_id_code}", True

        unique_id_code = generate_unique_id()

        self.redis.set(f"url:{unique_id_code}", url)
        self.redis.hset(UrlShortenerService.MAP_NAME, url, unique_id_code)

        return f"{settings.APP_DOMAIN}/{unique_id_code}", False

    def get_long_url_from_code(self, code: str) -> str:
        raw_long_url = self.redis.get(f"url:{code}")

        if raw_long_url is None:
            raise InvalidUrlException()

        long_url = str(raw_long_url)

        return long_url
