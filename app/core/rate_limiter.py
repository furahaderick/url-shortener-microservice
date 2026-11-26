import asyncio
import logging
from collections.abc import Coroutine
from typing import Any, cast

from fastapi import Depends, Request, Response
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Limiter, Rate, RedisBucket
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


def rate_limit(times: int, seconds: int):
    limiter_instance: RateLimiter | None = None
    initialization_lock = asyncio.Lock()

    bucket_key = f"app:rate-limit:{times}:{seconds}"

    async def dependency(req: Request, res: Response):
        nonlocal limiter_instance

        try:
            if limiter_instance is None:
                async with initialization_lock:
                    if limiter_instance is None:
                        rates = [Rate(times, Duration.SECOND * seconds)]

                        bucket = await cast(
                            Coroutine[Any, Any, RedisBucket],
                            RedisBucket.init(
                                rates,
                                req.app.state.redis,
                                bucket_key,
                            ),
                        )

                        limiter_instance = RateLimiter(limiter=Limiter(bucket))

            await limiter_instance(req, res)

        except RedisError as exc:
            logger.warning(
                "Redis unavailable; bypassing rate limiter",
                extra={"error_type": type(exc).__name__},
            )

    return Depends(dependency)
