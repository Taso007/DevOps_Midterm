#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# One-command environment preparation (Linux / macOS / Git-Bash).
#   ./scripts/bootstrap.sh
# Validates the environment, builds and starts the full stack, then runs the
# deployment-verification smoke test. Idempotent and reproducible.
# ---------------------------------------------------------------------------
set -euo pipefail

cd "$(dirname "$0")/.."

PY=python
command -v python >/dev/null 2>&1 || PY=python3

echo "==> [1/4] Preparing configuration"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "    created .env from .env.example"
else
  echo "    .env already exists"
fi

echo "==> [2/4] Validating environment"
$PY validate_env.py

echo "==> [3/4] Building and starting the stack"
docker compose up -d --build

echo "==> [4/4] Verifying deployment (smoke test)"
$PY smoke_test.py --url http://127.0.0.1:8000

cat <<'EOF'

============================================================
  Stack is up. Open:
    App (via proxy) : http://localhost:8000
    App blue        : http://localhost:8001
    App green       : http://localhost:8002
    Prometheus      : http://localhost:9090
    Grafana         : http://localhost:3001   (admin/admin)
    Kibana          : http://localhost:5601
    Elasticsearch   : http://localhost:9200
  Stop everything   : docker compose down
============================================================
EOF
