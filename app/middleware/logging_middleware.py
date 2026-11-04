import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()
        client_host = request.client.host if request.client else "unknown"

        logger.info(
            "Incoming request: %s %s from %s",
            request.method,
            request.url.path,
            client_host,
        )

        try:
            response = await call_next(request)

            processing_time = (time.time() - start_time) * 1000

            logger.info(
                "Completed request: %s %s Status: %s | Duration: %.2fms",
                request.method,
                request.url.path,
                response.status_code,
                processing_time,
            )

            return response

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(
                "Failed request: %s %s Error: %s | Duration: %.2fms",
                request.method,
                request.url.path,
                str(e),
                processing_time,
            )

            raise e
