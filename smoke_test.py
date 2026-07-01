#!/usr/bin/env python3
"""Deployment verification (smoke test).

Probes the running application through the proxy and asserts that every
critical endpoint behaves correctly. Used three ways:
  * by the bootstrap scripts, to confirm the stack came up healthy;
  * after `deploy.py`, as an automated post-deployment check;
  * in CI, against a container started from the freshly-built image.

Exits non-zero on the first failed check so it can gate automation.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request

GREEN, RED, RESET = "\033[92m", "\033[91m", "\033[0m"


def request(url, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.getcode(), resp.read().decode()


def wait_for_ready(base_url, retries, delay):
    """Block until /health responds 200 or retries are exhausted."""
    for attempt in range(1, retries + 1):
        try:
            code, _ = request(f"{base_url}/health")
            if code == 200:
                print(f"{GREEN}[ OK ]{RESET} service reachable after {attempt} attempt(s)")
                return True
        except (urllib.error.URLError, OSError) as e:
            print(f"  waiting for {base_url} ... ({attempt}/{retries}) {e}")
        time.sleep(delay)
    return False


def check(name, fn):
    try:
        fn()
        print(f"{GREEN}[ OK ]{RESET} {name}")
        return 0
    except AssertionError as e:
        print(f"{RED}[FAIL]{RESET} {name}: {e}")
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"{RED}[FAIL]{RESET} {name}: unexpected error: {e}")
        return 1


def run_checks(base_url):
    failures = 0

    def health():
        code, body = request(f"{base_url}/health")
        assert code == 200, f"expected 200, got {code}"
        assert json.loads(body)["status"] == "ok", "status != ok"

    def homepage():
        code, body = request(f"{base_url}/")
        assert code == 200, f"expected 200, got {code}"
        assert "DevOps Final" in body, "homepage marker missing"

    def dynamic_route():
        code, body = request(f"{base_url}/user/Smoke")
        assert code == 200, f"expected 200, got {code}"
        assert json.loads(body)["message"] == "Hello, Smoke!", "greeting mismatch"

    def submit():
        code, body = request(f"{base_url}/submit", "POST", {"data": "ping"})
        assert code == 201, f"expected 201, got {code}"
        assert json.loads(body)["received"] == "ping", "echo mismatch"

    def metrics():
        code, body = request(f"{base_url}/metrics")
        assert code == 200, f"expected 200, got {code}"
        assert "app_requests_total" in body, "metric app_requests_total missing"

    for name, fn in [
        ("GET /health", health),
        ("GET /", homepage),
        ("GET /user/:name", dynamic_route),
        ("POST /submit", submit),
        ("GET /metrics", metrics),
    ]:
        failures += check(name, fn)
    return failures


def main():
    parser = argparse.ArgumentParser(description="Smoke-test the deployed app.")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="base URL")
    parser.add_argument("--retries", type=int, default=20, help="readiness retries")
    parser.add_argument("--delay", type=float, default=3.0, help="seconds between retries")
    args = parser.parse_args()

    print(f"=== Smoke test against {args.url} ===")
    if not wait_for_ready(args.url, args.retries, args.delay):
        print(f"{RED}[FAIL]{RESET} service never became ready")
        sys.exit(1)

    failures = run_checks(args.url)
    print()
    if failures:
        print(f"{RED}{failures} check(s) failed — deployment verification FAILED.{RESET}")
        sys.exit(1)
    print(f"{GREEN}All checks passed — deployment verified.{RESET}")


if __name__ == "__main__":
    main()
