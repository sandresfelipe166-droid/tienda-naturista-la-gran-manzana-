import os
import sys

os.environ["TESTING"] = "true"

from typing import List, Tuple

from starlette.testclient import TestClient

# Ensure project root is on sys.path, then import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after setting TESTING to avoid real DB init
from main import app


def run_smoke_tests():
    client = TestClient(app)

    endpoints: list[tuple[str, str]] = [
        ("Root", "/"),
        ("API Info", "/api/v1/"),
        ("Health", "/api/v1/health"),
        ("Health Detailed", "/api/v1/health/detailed"),
        ("Inventory Summary", "/api/v1/inventory"),
    ]

    print("=== Smoke Test Start ===")
    for name, path in endpoints:
        try:
            resp = client.get(path)
            print(f"\n--- {name} [{path}] ---")
            print(f"Status: {resp.status_code}")
            # Print a subset of JSON to avoid very long output
            try:
                json_data = resp.json()
                if isinstance(json_data, dict):
                    keys_preview = {k: json_data[k] for k in list(json_data.keys())[:6]}
                else:
                    keys_preview = json_data
                print(f"JSON (preview): {keys_preview}")
            except Exception:
                print("No JSON body or failed to parse.")

            # Security headers check
            sec_headers = {
                "X-Content-Type-Options": resp.headers.get("X-Content-Type-Options"),
                "X-Frame-Options": resp.headers.get("X-Frame-Options"),
                "X-XSS-Protection": resp.headers.get("X-XSS-Protection"),
                "Referrer-Policy": resp.headers.get("Referrer-Policy"),
                "Permissions-Policy": resp.headers.get("Permissions-Policy"),
                "X-Powered-By": resp.headers.get("X-Powered-By"),
                "X-Environment": resp.headers.get("X-Environment"),
            }
            print(f"Security headers: {sec_headers}")

            # Rate limit headers check
            rl_headers = {
                "X-RateLimit-Limit": resp.headers.get("X-RateLimit-Limit"),
                "X-RateLimit-Remaining": resp.headers.get("X-RateLimit-Remaining"),
                "X-RateLimit-Window": resp.headers.get("X-RateLimit-Window"),
                "X-RateLimit-Reset": resp.headers.get("X-RateLimit-Reset"),
            }
            print(f"RateLimit headers: {rl_headers}")

            # Request ID header
            print(f"X-Request-Id: {resp.headers.get('X-Request-Id')}")
        except Exception as e:
            print(f"Error calling {path}: {e}")

    print("\n=== Smoke Test End ===")


if __name__ == "__main__":
    run_smoke_tests()
