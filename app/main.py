import logging
from datetime import UTC, datetime

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.dependencies import AsyncSessionDep
from app.core.exception_handlers import register_error_handlers
from app.core.logger import setup_logging
from app.middleware.logging_middleware import LoggingMiddleware
from app.routes.auth import router as auth_router
from app.routes.urls import router as url_router

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, summary=settings.APP_SUMMARY)

app.add_middleware(LoggingMiddleware)

# Register all error handlers
register_error_handlers(app)


@app.get("/health", tags=["Health Check"])
async def get_app_status(session: AsyncSessionDep):
    services = {
        "app": {"status": "healthy"},
        "postgres": {"status": "healthy"},
    }

    try:
        await session.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 # pylint: disable=W0718
        services["postgres"]["status"] = "unhealthy"

    healthy = all(services[name]["status"] == "healthy" for name in ("postgres",))

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
