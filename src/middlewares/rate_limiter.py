from fastapi import Request, HTTPException, status
import redis.asyncio as redis
from src.core.config import settings

redis_client = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)

async def rate_limiter(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    key = f"rate_limit:{client_ip}"
    try:
        current = await redis_client.incr(key)
        if current == 1:
            await redis_client.expire(key, settings.RATE_LIMIT_WINDOW_SECONDS)
        if current > settings.RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {settings.RATE_LIMIT_REQUESTS} req/{settings.RATE_LIMIT_WINDOW_SECONDS}s."
            )
    except redis.RedisError:
        pass