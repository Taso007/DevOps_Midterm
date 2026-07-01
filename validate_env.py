#!/usr/bin/env python3
"""Environment validation — fail fast before bringing the stack up.

Checks that the tools, files and ports the project needs are actually
available, and that the Docker Compose definition is valid. Run automatically
by the bootstrap scripts and reusable in CI.
"""
import shutil
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "docker-compose.yml",
    "Dockerfile",
    "package.json",
    "app.js",
    "proxy.js",
    "prometheus/prometheus.yml",
    "prometheus/alerts.yml",
    "logstash/pipeline/logstash.conf",
    "grafana/provisioning/datasources/datasource.yml",
    "config/active_env.json",
]

# Ports the stack binds on the host. Busy ports are warnings, not hard errors,
# because the conflicting service might be a previous run of this same stack.
PORTS = {
    8000: "reverse proxy",
    8001: "app-blue",
    8002: "app-green",
    9090: "prometheus",
    3001: "grafana",
    9200: "elasticsearch",
    5601: "kibana",
}

GREEN, RED, YELLOW, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[0m"


def ok(msg):
    print(f"{GREEN}[ OK ]{RESET} {msg}")


def warn(msg):
    print(f"{YELLOW}[WARN]{RESET} {msg}")


def fail(msg):
    print(f"{RED}[FAIL]{RESET} {msg}")


def check_tools():
    errors = 0
    if shutil.which("docker"):
        ok("docker is installed")
    else:
        fail("docker is not installed or not on PATH")
        errors += 1

    try:
        subprocess.run(
            ["docker", "compose", "version"],
            check=True, capture_output=True, text=True,
        )
        ok("docker compose plugin is available")
    except Exception:
        fail("`docker compose` is not available")
        errors += 1
    return errors


def check_files():
    errors = 0
    for rel in REQUIRED_FILES:
        if (ROOT / rel).exists():
            ok(f"found {rel}")
        else:
            fail(f"missing required file: {rel}")
            errors += 1
    return errors


def check_ports():
    for port, name in PORTS.items():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                warn(f"port {port} ({name}) is already in use")
            else:
                ok(f"port {port} ({name}) is free")
    return 0


def check_compose():
    try:
        subprocess.run(
            ["docker", "compose", "config", "--quiet"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        ok("docker-compose.yml is valid")
        return 0
    except subprocess.CalledProcessError as e:
        fail("docker-compose.yml failed validation:")
        print(e.stderr)
        return 1


def main():
    print("=== Environment validation ===")
    errors = 0
    errors += check_tools()
    errors += check_files()
    check_ports()
    if shutil.which("docker"):
        errors += check_compose()

    print()
    if errors:
        fail(f"{errors} blocking problem(s) found. Fix them before deploying.")
        sys.exit(1)
    ok("Environment looks good. You can run: docker compose up -d --build")


if __name__ == "__main__":
    main()
