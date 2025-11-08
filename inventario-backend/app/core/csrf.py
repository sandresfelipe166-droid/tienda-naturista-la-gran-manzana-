import base64
import hashlib
import hmac
import secrets
import time

from app.core.config import settings


def _make_signature(secret: str, payload: str) -> str:
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def generate_csrf_token(
    secret: str | None = None,
    expire_seconds: int | None = None,
    timestamp: int | None = None,
) -> str:
    """Generate a CSRF token signed with HMAC-SHA256.

    Token structure (before base64): "{timestamp}:{nonce}:{signature}" and then URL-safe base64 encoded.
    `timestamp` and `expire_seconds` are optional; tests may pass explicit timestamp.
    """
    secret = secret or settings.csrf_secret
    expire_seconds = expire_seconds or (settings.csrf_token_expire_minutes * 60)
    ts = int(timestamp if timestamp is not None else time.time())
    nonce = secrets.token_urlsafe(8)
    payload = f"{ts}:{nonce}"
    sig = _make_signature(secret, payload)
    token = f"{payload}:{sig}"
    return base64.urlsafe_b64encode(token.encode()).decode()


def validate_csrf_token(
    token: str, max_age_seconds: int | None = None, secret: str | None = None
) -> tuple[bool, int | None]:
    """Validate a CSRF token. Returns (is_valid, timestamp).

    is_valid is True when signature matches and token is not expired. timestamp is the token's ts if parseable.
    """
    secret = secret or settings.csrf_secret
    max_age_seconds = max_age_seconds or (settings.csrf_token_expire_minutes * 60)
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        parts = raw.split(":")
        if len(parts) < 3:
            return False, None
        ts_str, nonce, sig = parts[0], parts[1], parts[2]
        payload = f"{ts_str}:{nonce}"
        expected = _make_signature(secret, payload)
        # Use hmac.compare_digest for constant-time compare
        if not hmac.compare_digest(expected, sig):
            return False, None
        ts = int(ts_str)
        if max_age_seconds is not None:
            if int(time.time()) - ts > int(max_age_seconds):
                return False, ts
        return True, ts
    except Exception:
        return False, None
