import asyncio
import time
from datetime import datetime
from typing import Optional

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging_config import inventario_logger as logger


class RedisRateLimiter:
    """Rate limiter using Redis with sliding window implemented via sorted sets.

    Uses ZADD with timestamp as score and ZREMRANGEBYSCORE to remove old entries.
    Key format: ratelimit:{key}
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or (settings.get_redis_url() if settings.redis_host else None)
        self._client = None

    async def _get_client(self):
        if self._client is None:
            if not self.redis_url:
                raise RuntimeError("Redis URL not configured for RedisRateLimiter")
            self._client = await aioredis.from_url(self.redis_url, decode_responses=True)
        return self._client

    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check and add the current request. Returns True if allowed."""
        client = await self._get_client()
        now = time.time()
        window_start = now - window
        rkey = f"ratelimit:{key}"
        async with client.pipeline() as pipe:
            # Remove old entries
            await pipe.zremrangebyscore(rkey, 0, window_start)
            # Add current
            await pipe.zadd(rkey, {str(now): now})
            # Set TTL slightly larger than window
            await pipe.expire(rkey, window + 5)
            # Get count
            await pipe.zcard(rkey)
            res = await pipe.execute()
        count = int(res[-1]) if res and res[-1] is not None else 0
        return count <= limit

    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        client = await self._get_client()
        now = time.time()
        window_start = now - window
        rkey = f"ratelimit:{key}"
        await client.zremrangebyscore(rkey, 0, window_start)
        count = await client.zcard(rkey)
        return max(0, limit - int(count))

    async def get_reset_time(self, key: str, window: int) -> Optional[datetime]:
        client = await self._get_client()
        now = time.time()
        window_start = now - window
        rkey = f"ratelimit:{key}"
        # Get the smallest score (oldest) to compute reset
        members = await client.zrange(rkey, 0, 0, withscores=True)
        if not members:
            return None
        oldest_score = members[0][1]
        reset_ts = oldest_score + window
        return datetime.fromtimestamp(reset_ts)


# Helper to create a redis limiter instance (callers should await initialization)
async def create_redis_limiter():
    limiter = RedisRateLimiter()
    await limiter._get_client()
    return limiter
