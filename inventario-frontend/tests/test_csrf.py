import time

from app.core.csrf import generate_csrf_token, validate_csrf_token


def test_csrf_token_valid_and_parseable():
    token = generate_csrf_token(secret="test-secret", expire_seconds=60)
    valid, ts = validate_csrf_token(token, max_age_seconds=60, secret="test-secret")
    assert valid is True
    assert isinstance(ts, int)


def test_csrf_token_expired():
    # Create token with old timestamp
    old_ts = int(time.time()) - 3600
    token = generate_csrf_token(secret="test-secret", timestamp=old_ts)
    valid, ts = validate_csrf_token(token, max_age_seconds=60, secret="test-secret")
    assert valid is False
    assert ts == old_ts


def test_csrf_token_invalid_signature():
    token = generate_csrf_token(secret="test-secret")
    # Tamper token
    tampered = token[:-2] + "aa"
    valid, ts = validate_csrf_token(tampered, secret="test-secret")
    assert valid is False
    assert ts is None
