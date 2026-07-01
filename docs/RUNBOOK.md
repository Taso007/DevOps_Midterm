# Incident Response Runbook

How to detect, triage, and recover from common failures. The goal is fast,
predictable recovery using the automation already in this repo.

## 0. At a glance

| Symptom | Most likely cause | Fastest fix |
|---------|-------------------|-------------|
| Site returns `502 Bad Gateway` | Active app slot is down | `python rollback.py` |
| New release misbehaving | Bad deploy | `python rollback.py` (or it auto-rolls back) |
| `CriticalHighErrorRate` firing | App bug / dependency failure | Check Kibana logs → rollback or disable feature flag |
| New UI broken | Feature regression | Set `NEW_UI_ENABLED=false` and restart app |
| One container unhealthy | Crash / OOM | `docker compose restart <svc>` |

## 1. Detection

Incidents surface through three channels:

1. **Alerts** — Prometheus rules ([`prometheus/alerts.yml`](../prometheus/alerts.yml))
   visible at http://localhost:9090/alerts and in Grafana.
2. **Health monitor** — `python monitor.py` logs every check to `logs/health.log`
   (also viewable at `/logs`).
3. **Dashboards** — Grafana "DevOps Final — App Dashboard" (http://localhost:3001)
   shows instance up/down, error rate, and p95 latency.

## 2. Triage

```bash
docker compose ps                 # which containers are up / healthy
docker compose logs -f proxy      # proxy routing / 502s
docker compose logs -f logstash   # log pipeline
curl http://localhost:8000/health # is the service answering through the proxy?
```

Inspect application logs in **Kibana** (http://localhost:5601, data view
`app-logs-*`): filter `app.statusCode: 500` or `app.path: "/error"` to find the
failing requests. Check **Prometheus** for which slot is down (`up{job="app"}`).

## 3. Recovery procedures

### 3a. Roll back a bad deployment (primary procedure)

```bash
python rollback.py
```

Flips the proxy back to the previous slot. It runs a **safety health check** on
the target slot first and aborts if that slot is also unhealthy (prevents a
"false rollback" onto a broken version). Note: `deploy.py` already performs an
automated post-deployment smoke test and **auto-rolls-back** if verification
fails, so most bad releases never reach users.

### 3b. Disable a feature without redeploying

If the regression is behind the feature flag (Assignment 1 strategy):

```bash
# .env
NEW_UI_ENABLED=false
docker compose up -d app-blue app-green   # picks up the change, no rebuild
```

### 3c. Restart a crashed / unhealthy service

```bash
docker compose restart app-blue        # or app-green / proxy / prometheus ...
```

All services run with `restart: unless-stopped`, so Docker already restarts
crashed containers automatically; this is the manual override.

### 3d. Full-outage recovery (both slots down)

```bash
docker compose up -d --build           # rebuild + restart everything
python smoke_test.py                   # verify the service is healthy again
```

## 4. Verification (always do this after recovery)

```bash
python smoke_test.py --url http://127.0.0.1:8000
```

Confirms `/health`, `/`, `/user/:name`, `/submit`, and `/metrics` all behave.
Confirm in Grafana that error rate and latency have returned to baseline and the
alert has cleared in Prometheus.

## 5. Post-incident

- Capture the relevant Kibana logs and Grafana panels.
- Record root cause and the timeline.
- If the error budget (see [SLO.md](SLO.md)) was impacted, the next change must
  be a reliability fix before new feature work resumes.
