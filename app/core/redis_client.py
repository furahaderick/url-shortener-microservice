from redis.asyncio import Redis

from app.core.config import settings


# REDIS
def get_redis_url():
    host = settings.REDIS_HOST
    port = settings.REDIS_PORT
    db = settings.REDIS_DB
    return f"redis://{host}:{port}/{db}"


def create_redis_client() -> Redis:
    return Redis.from_url(get_redis_url(), decode_responses=True)
