from app.core.config import settings


def get_redis_url():
    host = settings.REDIS_HOST
    port = settings.REDIS_PORT
    db = settings.REDIS_DB
    return f"redis://{host}:{port}/{db}"
