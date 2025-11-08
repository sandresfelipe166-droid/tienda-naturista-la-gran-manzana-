from app.core.exceptions import (
    RateLimitException,
    SecurityException,
)


def test_rate_limit_exception():
    exc = RateLimitException(limit=10, window=60)
    assert exc.status_code == 429
    assert exc.details["limit"] == 10
    assert exc.details["window"] == 60


def test_security_exception():
    exc = SecurityException()
    assert exc.status_code == 403
    assert exc.message == "Security error"
