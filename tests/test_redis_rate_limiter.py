"""Tests for Redis-backed rate limiter."""

import os
import pytest
import redis.asyncio as redis
from unittest.mock import AsyncMock, patch

from app.core.rate_limiter_redis import RedisRateLimiter


@pytest.fixture
async def redis_limiter():
    """Fixture for Redis rate limiter."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Try to connect; if Redis is not available, skip tests
    try:
        r = await redis.from_url(redis_url)
        await r.ping()
        await r.close()
    except Exception as e:
        pytest.skip(f"Redis not available: {e}")
    
    limiter = RedisRateLimiter(
        redis_url=redis_url,
        max_requests=5,
        window_seconds=60,
    )
    yield limiter
    
    # Cleanup: close connection
    if limiter.redis:
        await limiter.redis.close()


@pytest.mark.asyncio
async def test_redis_rate_limiter_allow_requests(redis_limiter):
    """Test that Redis limiter allows requests within limit."""
    client_id = "test-client-1"
    
    for i in range(5):
        allowed = await redis_limiter.is_allowed(client_id)
        assert allowed is True, f"Request {i+1} should be allowed"


@pytest.mark.asyncio
async def test_redis_rate_limiter_blocks_excess(redis_limiter):
    """Test that Redis limiter blocks requests over limit."""
    client_id = "test-client-2"
    
    # Allow 5 requests
    for i in range(5):
        allowed = await redis_limiter.is_allowed(client_id)
        assert allowed is True
    
    # Next request should be blocked
    allowed = await redis_limiter.is_allowed(client_id)
    assert allowed is False, "Request 6 should be blocked"


@pytest.mark.asyncio
async def test_redis_rate_limiter_multiple_clients(redis_limiter):
    """Test that Redis limiter tracks separate clients."""
    client_1 = "test-client-a"
    client_2 = "test-client-b"
    
    # Fill client 1's quota
    for _ in range(5):
        allowed = await redis_limiter.is_allowed(client_1)
        assert allowed is True
    
    # Client 2 should still have quota
    allowed = await redis_limiter.is_allowed(client_2)
    assert allowed is True, "Client 2 should not be affected by Client 1's quota"
    
    # Client 1 should be blocked
    allowed = await redis_limiter.is_allowed(client_1)
    assert allowed is False, "Client 1 should be blocked"


@pytest.mark.asyncio
async def test_redis_rate_limiter_respects_custom_limits(redis_limiter):
    """Test that custom rate limit params work."""
    limiter = RedisRateLimiter(
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        max_requests=3,
        window_seconds=60,
    )
    
    try:
        client_id = "test-custom-limit"
        
        # Allow 3 requests
        for i in range(3):
            allowed = await limiter.is_allowed(client_id)
            assert allowed is True
        
        # 4th should be blocked
        allowed = await limiter.is_allowed(client_id)
        assert allowed is False
    finally:
        if limiter.redis:
            await limiter.redis.close()
