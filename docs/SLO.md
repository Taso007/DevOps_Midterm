# Service Level Objectives (SLOs)

These objectives define the reliability targets for the application and the
signals used to measure them. They are intentionally modest and demo-friendly,
but they map directly to real Prometheus metrics and alert rules in this repo.

## Service Level Indicators (SLIs)

| SLI | Definition | Prometheus source |
|-----|------------|--------------------|
| **Availability** | Fraction of time at least one app slot is scrapeable | `sum(up{job="app"}) > 0` |
| **Error rate** | Share of requests that result in 5xx / counted errors | `rate(app_errors_total[5m])` vs `rate(app_requests_total[5m])` |
| **Latency (p95)** | 95th-percentile request duration | `histogram_quantile(0.95, sum(rate(app_request_duration_seconds_bucket[5m])) by (le))` |

## Objectives

| Objective | Target (28-day window) | Error budget |
|-----------|------------------------|--------------|
| **Availability** | ≥ 99.5 % | ~3h 39m / 28 days |
| **Successful requests** | ≥ 99 % non-error | 1 % of requests |
| **Latency** | p95 < 500 ms | 5 % of minutes may exceed |

## Alerting policy (how SLOs are enforced)

The objectives are backed by the rules in [`prometheus/alerts.yml`](../prometheus/alerts.yml):

| Alert | Severity | Protects |
|-------|----------|----------|
| `AppInstanceDown` | CRITICAL | Availability (one slot down) |
| `AllInstancesDown` | CRITICAL | Availability (full outage) |
| `CriticalHighErrorRate` | CRITICAL | Error-rate objective (spike) |
| `ElevatedErrorRate` | WARNING | Error-rate objective (sustained) |
| `HighRequestLatencyP95` | WARNING | Latency objective |

WARNING alerts are early-warning signals (act before the budget is spent);
CRITICAL alerts indicate the objective is actively being breached and the
[runbook](RUNBOOK.md) should be followed.

## Error-budget policy

If the monthly error budget is exhausted, feature work pauses and the next
deployment must be a reliability fix. Releases continue normally while budget
remains. Deployments are gated by the CI quality + security checks and the
automated post-deployment smoke test, so a failing release is rolled back
automatically before it can burn budget.
