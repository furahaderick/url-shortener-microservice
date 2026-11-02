from contextlib import contextmanager

import redis

from app.core.database import get_redis_url


@contextmanager
def get_redis_client():
    client = redis.Redis.from_url(get_redis_url(), decode_responses=True)

    try:
        yield client
    finally:
        client.close()
