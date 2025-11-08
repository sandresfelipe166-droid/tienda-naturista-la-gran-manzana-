import os
import re
import sys

# Ensure TESTING mode
os.environ["TESTING"] = "true"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

client = TestClient(app)


def _is_safe_request_id(value: str) -> bool:
    if not value or len(value) > 128:
        return False
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    return all(ch in allowed for ch in value)


def test_rate_limit_headers_and_request_id_echo_on_root():
    # First request without custom request id
    r1 = client.get("/")
    assert r1.status_code in (200, 307, 308, 404) or r1.status_code < 500

    # Rate limit headers present
    for h in ("X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Window"):
        assert h in r1.headers and r1.headers[h] != ""

    # X-RateLimit-Reset may be present, if available
    # If present, should look like an ISO timestamp
    reset = r1.headers.get("X-RateLimit-Reset")
    if reset:
        # A simple check for ISO-like content (not strict)
        assert "T" in reset

    # Request id should be present and safe
    rid1 = r1.headers.get("X-Request-Id")
    assert rid1 and _is_safe_request_id(rid1)

    # Second request, Remaining should be <= previous remaining (same path/window)
    r2 = client.get("/")
    assert r2.status_code in (200, 307, 308, 404) or r2.status_code < 500

    # Check Remaining monotonic non-increasing
    rem1 = int(r1.headers["X-RateLimit-Remaining"])
    rem2 = int(r2.headers["X-RateLimit-Remaining"])
    assert rem2 <= rem1

    # Each request should get a request id (auto-generated) and differ if we didn't send one
    rid2 = r2.headers.get("X-Request-Id")
    assert rid2 and _is_safe_request_id(rid2)
    assert rid1 != rid2


def test_custom_request_id_is_echoed_if_safe():
    custom_id = "abc_123-XYZ"
    r = client.get("/", headers={"X-Request-Id": custom_id})
    assert r.status_code in (200, 307, 308, 404) or r.status_code < 500
    echoed = r.headers.get("X-Request-Id")
    assert echoed == custom_id
