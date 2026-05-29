"""
dependencies/rate_limit.py — Redis-backed rate limiting for write endpoints.

What it does:
  `check_rate_limit(request)` is a FastAPI dependency that enforces a
  sliding-window rate limit per client IP address using Redis INCR + EXPIRE.

  The internal `_redis_incr` function is intentionally extracted so tests can
  patch it with `patch("app.dependencies.rate_limit._redis_incr", ...)` without
  needing a real Redis connection.

Why it exists at this layer:
  Rate limiting belongs at the dependency layer — not in route handlers or CRUD.
  This keeps the router thin and makes the limit reusable across any endpoint.

How it connects:
  - app/routers/prayer_requests.py injects check_rate_limit on POST /prayer-requests.
  - app/config.py supplies upstash_redis_url and upstash_redis_token.
  - tests/test_prayer_requests.py patches _redis_incr to control count.

Security:
  - Limit: 3 submissions per IP per hour (configurable via RATE_LIMIT_MAX).
  - Key:   "rate:prayer:{client_ip}"
  - TTL:   3600 seconds (1 hour rolling window from first request)
  - Graceful degradation: if Redis is unavailable, the request is allowed
    through (fail-open) so a Redis outage doesn't block prayer submissions.
"""

import logging

from fastapi import HTTPException, Request, status

from app.config import settings

logger = logging.getLogger(__name__)

# Maximum prayer submissions per IP per hour.
RATE_LIMIT_MAX = 3
RATE_LIMIT_TTL = 3600  # seconds


def _redis_incr(key: str, ttl: int) -> int:
    """
    Increment `key` in Redis; set TTL on first write.
    Returns the new integer count after increment.

    Raises an exception (redis.RedisError or ConnectionError) if Redis
    is unavailable — callers should catch and fail-open.

    This function is a thin wrapper so tests can patch it:
      patch("app.dependencies.rate_limit._redis_incr", return_value=2)
    """
    import redis as redis_lib

    # Build client lazily (not at import time) so missing env vars don't
    # break the test suite when Redis is not configured.
    url   = settings.upstash_redis_url
    token = settings.upstash_redis_token

    if url and token:
        # Upstash Redis requires the token as the password.
        client = redis_lib.from_url(url, password=token, decode_responses=True)
    elif url:
        client = redis_lib.from_url(url, decode_responses=True)
    else:
        raise ConnectionError("UPSTASH_REDIS_URL not configured")

    pipe = client.pipeline()
    pipe.incr(key)
    pipe.expire(key, ttl, nx=True)  # Set TTL only if not already set (nx=True)
    count, _ = pipe.execute()
    return int(count)


async def check_rate_limit(request: Request) -> None:
    """
    FastAPI dependency — raises 429 if the client has exceeded the rate limit.

    Inject with: `Depends(check_rate_limit)`

    Fails open: if Redis is unavailable, the request proceeds normally.
    This is intentional — a Redis outage should not block prayer submissions.
    """
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate:prayer:{client_ip}"

    try:
        count = _redis_incr(key, RATE_LIMIT_TTL)
    except Exception as exc:
        # Fail-open: Redis unavailable → allow the request.
        logger.warning("Rate limit check skipped (Redis unavailable): %s", exc)
        return

    if count > RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Rate limit exceeded. You may submit up to {RATE_LIMIT_MAX} "
                f"prayer requests per hour."
            ),
        )
