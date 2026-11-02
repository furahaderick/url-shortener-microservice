from typing import Final
from fastapi import HTTPException, status
import redis

from app.schemas.url import UrlRequest
from app.utils import generate_unique_id

from app.core.config import settings


class UrlShortenerService:

    MAP_NAME: Final = "long_urls"

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def shorten_url(self, req: UrlRequest) -> str:
        # Check if the code for this url already exists
        url = str(req.url)
        existing_id_code = self.redis.hget(UrlShortenerService.MAP_NAME, url)

        if existing_id_code is not None:
            return f"{settings.APP_DOMAIN}/{existing_id_code}"

        unique_id_code = generate_unique_id()

        self.redis.set(f"url:{unique_id_code}", url)
        self.redis.hset(UrlShortenerService.MAP_NAME, url, unique_id_code)

        return f"{settings.APP_DOMAIN}/{unique_id_code}"

    def get_long_url_from_code(self, code: str) -> str:
        raw_long_url = self.redis.get(f"url:{code}")

        if raw_long_url is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL"
            )

        long_url = str(raw_long_url)

        return long_url
