import json
import os
import sys

# Ensure TESTING mode for predictable config
os.environ["TESTING"] = "true"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import settings  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)


def test_security_headers_presence_on_root():
    resp = client.get("/")
    assert resp.status_code in (200, 307, 308, 404) or resp.status_code < 500

    headers = resp.headers

    # Core security headers present
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Referrer-Policy" in headers
    assert "Permissions-Policy" in headers

    # Environment header
    assert headers.get("X-Environment") == settings.environment

    # Powered-By should be absent by default (send_x_powered_by=false)
    assert "X-Powered-By" not in headers

    # CSP is disabled by default unless enabled via settings
    assert ("Content-Security-Policy" in headers) == getattr(settings, "csp_enabled", False)
