#!/usr/bin/env python3
"""Blue-green deployment with automated post-deployment verification.

Flow:
  1. Read the currently active slot from config/active_env.json.
  2. Start the new version on the inactive slot (local mode) and health-check it.
  3. Flip the proxy config so live traffic moves to the new slot.
  4. Run an automated smoke test through the proxy (deployment verification).
  5. If verification fails, AUTOMATICALLY roll the config back to the previous
     slot (failure-recovery automation) so the live site stays stable.

In Docker mode both slots are already running; this script's config flip is
what the proxy honours to switch traffic.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

CONFIG_FILE = "config/active_env.json"
PROXY_URL = os.environ.get("PROXY_URL", "http://127.0.0.1:8000")
SKIP_VERIFY = os.environ.get("SKIP_VERIFY") == "1"


def read_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def write_config(port, env):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"port": port, "env": env}, f)


def health(port, retries=5):
    for i in range(retries):
        time.sleep(2)
        print(f"Health check attempt {i + 1}/{retries}...")
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/health", timeout=2
            ) as resp:
                if resp.getcode() == 200:
                    return True
        except Exception:
            continue
    return False


def post_deploy_verify():
    """Run the smoke test against the proxy. Returns True on success."""
    print("Running post-deployment verification (smoke test)...")
    result = subprocess.run(
        [sys.executable, "smoke_test.py", "--url", PROXY_URL, "--retries", "5", "--delay", "2"]
    )
    return result.returncode == 0


def main():
    print("Starting Blue-Green Deployment...")

    if not os.path.exists(CONFIG_FILE):
        print("Config file not found. Have you run setup.py?")
        sys.exit(1)

    config = read_config()
    current_port = config.get("port", 8001)
    current_env = config.get("env", "blue")

    target_port = 8002 if current_port == 8001 else 8001
    target_env = "green" if current_env == "blue" else "blue"

    print(f"Current Active Env: {current_env} (Port {current_port})")
    print(f"Deploying to Target Env: {target_env} (Port {target_port})...")

    # Start the target instance in the background (local mode).
    env = os.environ.copy()
    env["PORT"] = str(target_port)
    env["APP_ENV"] = target_env
    env["SERVICE_NAME"] = f"app-{target_env}"
    env["NODE_ENV"] = "production"
    creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
    subprocess.Popen(["node", "server.js"], env=env, creationflags=creationflags)

    print(f"Application started on port {target_port}. Verifying instance health...")
    if not health(target_port):
        print("Error: Target environment failed health check. Deployment aborted.")
        sys.exit(1)

    # Switch live traffic by flipping the proxy config.
    write_config(target_port, target_env)
    print(f"Traffic switched to {target_env} environment.")

    # Automated post-deployment verification through the proxy.
    if SKIP_VERIFY:
        print("SKIP_VERIFY=1 — skipping post-deployment smoke test.")
    elif not post_deploy_verify():
        print("Post-deployment verification FAILED. Auto-rolling back...")
        write_config(current_port, current_env)
        print(f"Rolled back to previous stable env: {current_env} (Port {current_port}).")
        sys.exit(1)

    print("Blue-Green deployment complete and verified!")


if __name__ == "__main__":
    main()
