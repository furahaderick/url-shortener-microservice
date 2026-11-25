import json

from redis.asyncio import Redis


class CacheService:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, key: str) -> dict | None:
        value = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def set(self, key: str, value: dict, ttl: int = 3600) -> None:
        await self.redis.set(key, json.dumps(value), ex=ttl)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self.redis.exists(key))
