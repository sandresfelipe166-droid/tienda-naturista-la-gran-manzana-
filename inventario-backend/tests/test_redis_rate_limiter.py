"""Tests for Redis-backed rate limiter."""

import os

import pytest
import pytest_asyncio
import redis.asyncio as redis

from app.core.rate_limiter_redis import RedisRateLimiter


@pytest_asyncio.fixture
async def redis_limiter():
    """Fixture for Redis rate limiter."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Try to connect; if Redis is not available, skip tests
    try:
        # Agregar socket_timeout para evitar que se quede cargando
        r = await redis.from_url(redis_url, socket_timeout=2.0, socket_connect_timeout=2.0)
        await r.ping()
        # Limpiar la base de datos del Redis de pruebas para evitar interferencias entre ejecuciones
        try:
            await r.flushdb()
        except Exception:
            pass
        await r.aclose()
    except Exception as e:
        pytest.skip(f"Redis not available: {e}")

    limiter = RedisRateLimiter(redis_url=redis_url)
    yield limiter

    # Cleanup: close connection
    client = await limiter._get_client()
    if client:
        try:
            await client.aclose()
        except Exception:
            pass


@pytest.mark.asyncio
@pytest.mark.integration
async def test_redis_rate_limiter_allow_requests(redis_limiter):
    """Test that Redis limiter allows requests within limit."""
    client_id = "test-client-1"
    limit = 5
    window = 60

    for i in range(limit):
        allowed = await redis_limiter.is_allowed(client_id, limit=limit, window=window)
        assert allowed is True, f"Request {i+1} should be allowed"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_redis_rate_limiter_blocks_excess(redis_limiter):
    """Test that Redis limiter blocks requests over limit."""
    client_id = "test-client-2"
    limit = 5
    window = 60

    # Allow 5 requests
    for i in range(limit):
        allowed = await redis_limiter.is_allowed(client_id, limit=limit, window=window)
        assert allowed is True

    # Next request should be blocked
    allowed = await redis_limiter.is_allowed(client_id, limit=limit, window=window)
    assert allowed is False, "Request 6 should be blocked"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_redis_rate_limiter_multiple_clients(redis_limiter):
    """Test that Redis limiter tracks separate clients."""
    client_1 = "test-client-a"
    client_2 = "test-client-b"
    limit = 5
    window = 60

    # Fill client 1's quota
    for _ in range(limit):
        allowed = await redis_limiter.is_allowed(client_1, limit=limit, window=window)
        assert allowed is True

    # Client 2 should still have quota
    allowed = await redis_limiter.is_allowed(client_2, limit=limit, window=window)
    assert allowed is True, "Client 2 should not be affected by Client 1's quota"

    # Client 1 should be blocked
    allowed = await redis_limiter.is_allowed(client_1, limit=limit, window=window)
    assert allowed is False, "Client 1 should be blocked"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_redis_rate_limiter_respects_custom_limits(redis_limiter):
    """Test that custom rate limit params work."""
    client_id = "test-custom-limit"
    custom_limit = 3
    window = 60

    # Allow 3 requests
    for i in range(custom_limit):
        allowed = await redis_limiter.is_allowed(client_id, limit=custom_limit, window=window)
        assert allowed is True

    # 4th should be blocked
    allowed = await redis_limiter.is_allowed(client_id, limit=custom_limit, window=window)
    assert allowed is False
