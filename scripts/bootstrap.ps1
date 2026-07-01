# ---------------------------------------------------------------------------
# One-command environment preparation (Windows PowerShell).
#   .\scripts\bootstrap.ps1
# Validates the environment, builds and starts the full stack, then runs the
# deployment-verification smoke test. Idempotent and reproducible.
# ---------------------------------------------------------------------------
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$py = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }

Write-Host "==> [1/4] Preparing configuration"
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "    created .env from .env.example"
} else {
    Write-Host "    .env already exists"
}

Write-Host "==> [2/4] Validating environment"
& $py validate_env.py
if ($LASTEXITCODE -ne 0) { throw "Environment validation failed" }

Write-Host "==> [3/4] Building and starting the stack"
docker compose up -d --build
if ($LASTEXITCODE -ne 0) { throw "docker compose up failed" }

Write-Host "==> [4/4] Verifying deployment (smoke test)"
& $py smoke_test.py --url http://127.0.0.1:8000
if ($LASTEXITCODE -ne 0) { throw "Smoke test failed" }

Write-Host @"

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
"@
