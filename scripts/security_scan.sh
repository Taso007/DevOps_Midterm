#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Local security scan — the same checks the CI security pipeline runs, but on
# your machine. All scanners run as throwaway Docker containers, so nothing
# needs to be installed beyond Docker itself. 100% free tooling.
#
#   bash scripts/security_scan.sh
#
# Scans performed:
#   1. npm audit            - dependency vulnerability scanning
#   2. Gitleaks             - secrets scanning (working tree)
#   3. Hadolint             - Dockerfile best-practice / security linting
#   4. Trivy (config)       - Dockerfile + compose misconfiguration scanning
#   5. Trivy (filesystem)   - deps + IaC + secret scanning
#   6. Trivy (image)        - container image CVE scanning (if image is built)
# ---------------------------------------------------------------------------
set -uo pipefail
export MSYS_NO_PATHCONV=1   # keep Windows Git-Bash from mangling /paths

cd "$(dirname "$0")/.."
REPO="$(pwd)"
FAILURES=0
WARNINGS=0
section() { echo; echo "============================================================"; echo "  $1"; echo "============================================================"; }
note()    { echo ">> $1"; }

section "1/6  npm audit — dependency vulnerabilities (production)"
# Capture output so we can tell a genuine vulnerability finding apart from a
# registry/TLS failure (e.g. a corporate proxy or antivirus doing SSL
# inspection), which npm otherwise reports with the same non-zero exit code.
audit_out="$(npm audit --omit=dev --audit-level=high 2>&1)"; audit_rc=$?
echo "$audit_out"
if [ "$audit_rc" -eq 0 ]; then
  note "no high/critical production dependency vulnerabilities"
elif printf '%s\n' "$audit_out" | grep -qiE \
     'audit endpoint returned an error|unable to verify the first certificate|self[ -]signed certificate|request to .* failed|ENOTFOUND|ETIMEDOUT|ECONNREFUSED|ECONNRESET|EAI_AGAIN|UNABLE_TO_VERIFY|SELF_SIGNED_CERT|network'; then
  note "npm audit could NOT reach the registry (network/TLS error) — skipped, not a security failure."
  note "the same dependencies are scanned offline by Trivy (step 5, package-lock.json)."
  WARNINGS=$((WARNINGS+1))
else
  note "npm audit reported high/critical vulnerabilities"; FAILURES=$((FAILURES+1))
fi

section "2/6  Gitleaks — secrets scanning"
if docker run --rm -v "$REPO:/repo" zricethezav/gitleaks:latest \
     detect --source=/repo --config=/repo/.gitleaks.toml --no-git -v; then
  note "no secrets detected"
else
  note "gitleaks detected potential secrets"; FAILURES=$((FAILURES+1))
fi

section "3/6  Hadolint — Dockerfile linting"
if docker run --rm -i hadolint/hadolint < Dockerfile; then
  note "Dockerfile passed hadolint"
else
  note "hadolint reported Dockerfile issues"; FAILURES=$((FAILURES+1))
fi

section "4/6  Trivy — IaC / config misconfiguration"
if docker run --rm -v "$REPO:/src" aquasec/trivy:latest \
     config --exit-code 1 --severity HIGH,CRITICAL /src; then
  note "no high/critical misconfigurations"
else
  note "trivy config found misconfigurations"; FAILURES=$((FAILURES+1))
fi

section "5/6  Trivy — filesystem (deps + secrets)"
if docker run --rm -v "$REPO:/src" aquasec/trivy:latest \
     fs --scanners vuln,secret --exit-code 1 --severity HIGH,CRITICAL /src; then
  note "filesystem scan clean"
else
  note "trivy fs found high/critical issues"; FAILURES=$((FAILURES+1))
fi

section "6/6  Trivy — container image"
if docker image inspect devops-final-app:latest >/dev/null 2>&1; then
  if docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest \
       image --exit-code 1 --severity HIGH,CRITICAL devops-final-app:latest; then
    note "image scan clean"
  else
    note "trivy image found high/critical CVEs"; FAILURES=$((FAILURES+1))
  fi
else
  note "image devops-final-app:latest not built yet — run 'docker compose build' first (skipped)"
fi

section "Summary"
if [ "$FAILURES" -eq 0 ]; then
  if [ "$WARNINGS" -gt 0 ]; then
    echo "No security findings, but $WARNINGS check(s) could not run (see warnings above)."
  else
    echo "All security scans passed."
  fi
else
  echo "$FAILURES scan(s) reported findings. Review the output above."
  exit 1
fi
