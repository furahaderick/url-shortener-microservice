from typing import Final, cast

import redis

from app.repositories.interfaces import UrlCacheRepository


class RedisUrlCacheRepo(UrlCacheRepository):
    MAP_NAME: Final = "long_urls"

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def get_code_by_url(self, url: str) -> str | None:
        result = self.redis.hget(self.MAP_NAME, url)

        return cast(str | None, result)

    def save_url(self, code: str, url: str) -> None:
        self.redis.set(f"url:{code}", url)
        self.redis.hset(self.MAP_NAME, url, code)

    def get_url_by_code(self, code: str) -> str | None:
        result = self.redis.get(f"url:{code}")

        return cast(str | None, result)
