import logging

from fastapi import FastAPI

from app.core.config import settings
from app.routes.urls import router as url_router
from app.exception_handlers import register_error_handlers
from app.logger import setup_logging
from app.middleware.logging_middleware import LoggingMiddleware

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, summary=settings.APP_SUMMARY)

app.add_middleware(LoggingMiddleware)

# Register all error handlers
register_error_handlers(app)


@app.get("/health", tags=["Health Check"])
def get_app_status():
    return {"Status": "Alive"}


app.include_router(url_router)
