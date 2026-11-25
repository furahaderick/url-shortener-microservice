import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.dependencies import AsyncSessionDep, RedisDep
from app.core.exception_handlers import register_error_handlers
from app.core.logger import setup_logging
from app.core.redis_client import create_redis_client
from app.middleware.logging_middleware import LoggingMiddleware
from app.routes.analytics import router as analytics_router
from app.routes.auth import router as auth_router
from app.routes.urls import router as url_router

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.redis = create_redis_client()

    try:
        yield
    finally:
        await application.state.redis.aclose()


app = FastAPI(lifespan=lifespan, title=settings.APP_NAME, summary=settings.APP_SUMMARY)

app.add_middleware(LoggingMiddleware)

# Register all error handlers
register_error_handlers(app)


@app.get("/health", tags=["Health Check"])
async def get_app_status(
    session: AsyncSessionDep,
    redis: RedisDep,
) -> JSONResponse:

    services = {
        "app": {"status": "healthy"},
        "postgres": {"status": "healthy"},
        "redis": {"status": "healthy"},
    }

    # PostgreSQL health check
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        services["postgres"]["status"] = "unhealthy"

    # Redis health check
    key = f"health:{uuid4()}"

    try:
        await redis.set(key, "hello", ex=10)
        value = await redis.get(key)

        if value != "hello":
            services["redis"]["status"] = "unhealthy"

    except RedisError:
        services["redis"]["status"] = "unhealthy"

    finally:
        try:
            await redis.delete(key)
        except RedisError:
            services["redis"]["status"] = "unhealthy"

    # PostgreSQL is mandatory; Redis is mandatory.
    healthy = all(
        services[name]["status"] == "healthy" for name in ("postgres", "redis")
    )

    return JSONResponse(
        status_code=(
            status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
        content={
            "status": "healthy" if healthy else "degraded",
            "timestamp": datetime.now(UTC).isoformat(),
            "services": services,
        },
    )


app.include_router(auth_router)
app.include_router(url_router)
app.include_router(analytics_router)
