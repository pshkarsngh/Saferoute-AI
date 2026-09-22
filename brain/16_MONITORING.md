# 16_MONITORING.md — SafeRoute AI Monitoring & Observability Specification

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Authoritative Monitoring & Observability Specification
**Version:** 1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_RULES.md` > `01_PRD.md` > `02_TRD.md` > `09_ERROR_HANDLING.md` > `15_DEPLOYMENT.md` > this document
**Companion:** `09_ERROR_HANDLING.md` §12–§16 (logging/classification/alerting/incident flow), `15_DEPLOYMENT.md` (deploy-time watchlist), `10_SECURITY.md`, `13_TESTING.md`

Any unresolved observability decision in this document is marked `[DECISION REQUIRED]` with the missing decision, why it matters, options, and affected documents.

---

## 1. PURPOSE

This document defines what SafeRoute AI measures, logs, correlates, and alerts on so that the system can be operated, diagnosed, and held accountable in production. It covers:

- Metrics (counters, durations, rates)
- Structured logging fields and the exact never-log list
- Severity mapping
- Correlation via `request_id`
- Exit status taxonomy
- Alerting thresholds
- Health-endpoint behavior
- Auditability and reproducibility
- Incident diagnosis flow

It does not define how the system deploys (`15_DEPLOYMENT.md`) or how the system handles errors at the application level (`09_ERROR_HANDLING.md`); this document consumes those definitions.

---

## 2. METRICS

Metrics follow `02_TRD.md` §159 and `09_ERROR_HANDLING.md` §14. All metrics carry labels where meaningful (e.g., `error_code`, `stage`, `provider`, `model_version`, `route_count`).

| Metric                       | Type      | What it captures                                              |
|------------------------------|-----------|---------------------------------------------------------------|
| `route_requests_total`       | Counter   | Route-generation requests received (POST /api/routes)         |
| `route_generation_failures`  | Counter   | Failed route-generation attempts (provider error, no route)   |
| `analysis_requests_total`    | Counter   | Analysis jobs/runs requested (POST analyze)                   |
| `analysis_failures`          | Counter   | Analysis runs that ended in `failed` (vs partial)             |
| `analysis_requests_failures` | Counter   | Alias used where job-level failure accounting is separate; counted when analysis ends `failed` |
| `yolo_inference_count`       | Counter   | YOLO11 inferences executed; labeled by `model_version`        |
| `yolo_inference_duration`    | Histogram | YOLO11 per-image inference latency (seconds)                  |
| `facility_requests_total`    | Counter   | Facility provider searches issued                            |
| `facility_failures`          | Counter   | Facility provider failures (`status=unavailable`)             |
| `llm_requests_total`         | Counter   | LLM generation calls issued                                  |
| `llm_failures`               | Counter   | LLM failures resulting in fallback text                       |
| `average_analysis_duration`  | Histogram | End-to-end analysis duration by job (minutes/seconds)         |
| `error_rate`                 | Gauge/rate| Error rate per `error_code` (e.g., `error_rate{error_code="YOLO_INFERENCE_FAILED"}`) |
| `partial_analysis_count`     | Counter   | Analyses that returned the partial envelope (`status=partial`) |
| `cache_hit_rate`             | Gauge     | Cache hit ratio per cache domain (route, image, facility, analysis) |
| `queue_latency`              | Histogram | Time a job waits before worker pickup (if an ML worker exists) |
| `model_inference_latency`    | Histogram | Inference latency at the model boundary (worker/service)      |

Additional observed signals (not fundamentally metrics, but tracked): provider 5xx/429 counts per provider, DB connection failures, model load failures (`MODEL_LOAD_FAILED`), `SECURITY_VIOLATION` occurrences, rate-limit rejections on our API.

Metrics are exported via the standard instrumentation path (`[DECISION REQUIRED]`: Prometheus `/metrics` vs platform-native exporter; low-traffic v1 can export `/metrics` without an external scraper) and consumed by the alerting rules in §8.

---

## 3. STRUCTURED LOGGING

Logs are structured (JSON lines preferred) using the canonical field set (`09_ERROR_HANDLING.md` §12.1, `02_TRD.md` §78):

```json
{
  "ts": "2026-09-22T10:15:30.123Z",
  "level": "error",
  "service": "backend",
  "request_id": "req_123",
  "route_id": "route_1",
  "job_id": "job_456",
  "stage": "YOLO_INFERENCE",
  "duration_ms": 1823,
  "error_code": "YOLO_INFERENCE_FAILED",
  "error_type": "provider",
  "provider": "yolo11",
  "status": "failed",
  "model_version": "1.0.0",
  "configuration_version": "2026-09-01"
}
```

**Field rules:**
- `ts` — RFC3339 UTC timestamp.
- `level` — DEBUG / INFO / WARNING / ERROR / CRITICAL (§4).
- `service` — emitting component (`backend`, `frontend`, `worker`, `db`).
- `request_id` — correlation carrier; present on every request-started log line (§6).
- `route_id`, `job_id` — filled when in scope, else omitted/null.
- `stage` — pipeline stage (`ROUTE_GENERATION`, `IMAGE_RETRIEVAL`, `OPENCV`, `YOLO_INFERENCE`, `HAZARD_AGGREGATION`, `RISK_CALCULATION`, `FACILITY_ANALYSIS`, `LLM_EXPLANATION`, `PROFILE`, `DB`).
- `duration_ms` — stage or request duration.
- `error_code` — stable code from `09_ERROR_HANDLING.md` §8.
- `error_type` — coarse category (validation | provider | model | config | timeout | rate_limit | internal | security).
- `provider` — routing/osrm | facility/overpass | llm/openai-compatible | imagery | yolo11 | database.
- `status` — outcome from §5.
- `model_version`, `configuration_version` — version tags for reproducibility (§10).

### 3.1 Exact never-log list

The following MUST never appear in logs, exception messages included, in any form (plaintext, encoded, masked-partially, or in stack traces):

- API keys (routing, imagery, facility, LLM, map)
- Passwords and password hashes
- Authentication tokens / bearer tokens / refresh tokens
- Database credentials and full connection strings with credentials
- JWT secrets / signing keys
- Internal paths that reveal infrastructure (e.g., `/etc/secrets/...`, absolute filesystem roots, internal k8s/service paths)
- Unnecessary coordinates (full lat/lon pairs beyond the operational need; log route_id/segment_id/masked references instead — `MASTER_PROJECT_PROMPT.md` §88, `09_ERROR_HANDLING.md` §12.1)
- Client secrets, private keys, payslips — any credential-like value

Enforcement: a log-line sanitizer runs at the logging boundary (field allow-list + reject rules), and CI runs a secret-pattern scan over code and test logs (`10_SECURITY.md`). Any accidental secret exposure triggers `runbooks/credential-reevocation-or-leak.md`.

---

## 4. SEVERITY MAPPING

Mapping follows `09_ERROR_HANDLING.md` §6 and §12.2:

| Level | Meaning | Examples |
|-------|---------|----------|
| INFO | Expected, benign, or informational events | Request started/completed, low-confidence detection dropped, provider 429 received and handled, cache hit |
| WARNING | Subsystem degradation that may not invalidate the overall result | One image invalid, provider blip recovered by retry, facility data unavailable, LLM fell back |
| ERROR | An operation failed; user action or recovery may be required | Risk not calculated, route generation failed, DB call failed |
| CRITICAL | Major failure, security incident, data-corruption risk, or service-wide failure | Model cannot load, database down, `SECURITY_VIOLATION` pattern, config fail at startup |

Severity drives logging sinks, retention, and alerting (CRITICAL → page, §8). It is deliberately distinct from the user-visible `analysis.status` (`09_ERROR_HANDLING.md` §6).

---

## 5. EXIT STATUSES

Every logical unit of work (request, job, stage, provider call) ends in exactly one of (`09_ERROR_HANDLING.md` §12.3):

- `succeeded` — completed fully as intended.
- `partial` — completed with at least one domain unavailable/failed (partial envelope returned).
- `failed` — operation failed and no usable result was produced.
- `unavailable` — the data/service was not producible (e.g., imagery unavailable, provider down, explicitly distinct from zero).
- `cancelled` — aborted by user/job cancellation before completion.
- `timed_out` — aborted by timeout (no silent hang; `09_ERROR_HANDLING.md` §10.10).

No log line for a completed operation may omit the status. The mapping to domains (route / safety / facilities / llm) uses the per-domain status chips of `09_ERROR_HANDLING.md` §13 and the frontend states of `08_UI_SPEC.md` §14.

---

## 6. CORRELATION

- The backend generates a `request_id` per top-level request (or echoes an inbound `X-Request-ID`), and it MUST:
  - Flow through every pipeline stage (route generation, image pipeline, YOLO, risk, facilities, LLM) via the structured logging field set.
  - Appear in every error envelope returned to the client (`09_ERROR_HANDLING.md` §9).
  - Be surfaced to the frontend and user (support info) so a support ticket can be traced (`09_ERROR_HANDLING.md` §13, §16).
  - Propagate into async job records (`job_id` linked to `request_id`) and any worker logs.
- `route_id` and `segment_id` further subgroup a request when multiple routes are analyzed concurrently (`02_TRD.md` §88).
- Frontend logs/telemetry attach the same `request_id` so backend and client traces join at the point of failure.
- The correlation contract is: `request_id` → stages → error envelope → frontend → logs. If any link is missing, correlation is broken and must be fixed before release.

---

## 7. AUDITABILITY AND REPRODUCIBILITY

Per `MASTER_PROJECT_PROMPT.md` §65–§66 and `02_TRD.md` §133–§134, §162–§164, persist on every analysis and record in logs/metrics:

- `model_version` (YOLO artifact name + version + dataset version + threshold)
- `risk_engine_version` (formula/weights version)
- `configuration_version` (risk weights, search radius, thresholds, route limits as a release-pinned config version)
- provider identifiers (routing, imagery, facility) and the LLM provider + LLM model/version
- timestamps (request, each stage, completion)
- input references: route, segment, image IDs used

This makes any analysis reproducible: route data + image IDs + model version + risk configuration + facility configuration (`02_TRD.md` §163) and lets the team attribute an anomaly to app bug, provider outage, or config/model change (§11).

---

## 8. ALERTING THRESHOLDS

Alerting rules from `09_ERROR_HANDLING.md` §14 with operational thresholds:

| Condition | Severity | Action |
|-----------|----------|--------|
| YOLO/model load failure (`MODEL_LOAD_FAILED`, `model` not loaded for > 1 min) | CRITICAL | **Page** (on-call); mark safety unavailable; block analysis that requires the model |
| Database unavailability (readiness fails, DB connection count > threshold) | CRITICAL | **Page**; API intends 503 with `DATABASE_ERROR`; no fabricated results |
| Model inference latency p95 above baseline (e.g., > 300% of staged baseline) sustained 10 min | WARNING | Alert; investigate device/CUDA/batching |
| Sustained provider failures (routing/facility/LLM) above threshold (e.g., > 25% failures over 10 min window) | WARNING | Alert, do not page; isolate subsystem; check provider status page |
| `error_rate{error_code="INTERNAL_ERROR"}` spike (e.g., > 2× baseline) | WARNING→CRITICAL | Alert then page on persistence; investigate + incident runbook |
| `SECURITY_VIOLATION` occurrences increase (e.g., > 5 in 10 min or any novel pattern) | CRITICAL | Alert + incident flow; consult `10_SECURITY.md` and `runbooks/` |
| `partial_analysis_count` ratio trending up (e.g., partial/total ratio > 25% over 30 min) | WARNING | Attention; find dominant failing domain via `error_rate` labels |
| Queue latency (worker) above threshold sustained (e.g., median job wait > 60 s) | WARNING | Alert; scale/investigate worker back-pressure |
| Route-generation failure rate spike (e.g., > 20% over 10 min) | WARNING | Alert; routing provider or config |
| Cache hit rate collapse (e.g., > 20 pts below baseline for 15 min) | WARNING | Alert; cache config/version-key drift |

Rules are data-driven: thresholds are baselined in staging before production; flakes are tuned out, not silenced. Alert storms are avoided by requiring sustained conditions (windowed) rather than single events except for CRITICAL pages.

---

## 9. HEALTH ENDPOINT BEHAVIOR

`GET /api/v1/health` (see `15_DEPLOYMENT.md` §8, `07_API_CONTRACT.md` §7.17) is the monitored health signal.

- Returns `status` (healthy/degraded/unhealthy) and per-component availability: database, model, providers (not_checked by default to avoid provider calls — `02_TRD.md` §158).
- NEVER leaks internals: no credentials, connection strings, internal paths, stack traces, or exact internal URLs (`09_ERROR_HANDLING.md` §4.11).
- Ready instances only receive traffic; liveness keeps the process reporting even when degraded so operators can inspect it.
- Monitored in CI post-deploy and by the orchestrator/load balancer; a flapping/unhealthy endpoint triggers the CRITICAL pages in §8.

---

## 10. LOG RETENTION AND AUDIT TRAIL

- Logs are retained per environment: development short-lived; staging moderate retention for release validation; production retention sufficient for incident reconstruction (policy value `[DECISION REQUIRED]` — legal/operational trade-off; recommend ≥ 30 days warm, ≥ 12 months cold for analysis records).
- The audit trail (analysis records with version tags per §7) is treated as data, backed up with the database (`15_DEPLOYMENT.md` §10).
- Logs never contain the never-log items (§3.1); the audit trail includes request_id, route_id, model/risk/config versions, provider, LLM model/version, and timestamps for reproducibility.

---

## 11. INCIDENT DIAGNOSIS FLOW

Flow per `09_ERROR_HANDLING.md` §16, made operational here:

1. **Find the `request_id`** — from the user's support info (error envelope / frontend state) or log search.
2. **Trace stages** — follow `request_id` (+ `route_id`, `job_id`) through the structured log; note stage sequence, durations, and status per stage.
3. **Read the failure signal** — `error_code`, `stage`, `provider`, `model_version`, `configuration_version` on the failing lines.
4. **Classify** — is this an **app bug** (INTERNAL_ERROR, validation crash, frontend mismatch), a **provider outage** (sustained *_PROVIDER_ERROR / facility/LLM/routing failures, provider status page), or a **config/model issue** (model_version/configuration_version drift, MODEL_LOAD_FAILED, class mismatch, resource exhaustion)?
5. **Use partial-status flags** — see which domains succeeded (`succeeded`/`partial`) vs failed (`unavailable`/`failed`) to bound blast radius.
6. **Consult metrics + alerts** — `error_rate` by code, provider failure gauges, latency histograms, cache hit rate, queue latency; check alert banners for sustained conditions.
7. **Replay/verify** — re-run the analysis with identical versions to confirm reproducibility or drift (audit trail §7).
8. **Remediate** — smallest correct change (deploy fix / provider mitigation / model or config rollback per `15_DEPLOYMENT.md` §11); re-run error-path tests (`13_TESTING.md`, `09_ERROR_HANDLING.md` §15); update docs if behavior changed.
9. **Record** — log the incident and update `16_CHANGELOG.md`; escalate to `runbooks/database-migration-failure.md` or `runbooks/credential-reevocation-or-leak.md` when applicable.

---

## 12. RELATED DOCUMENTS

- `09_ERROR_HANDLING.md` §12–§16 — logging fields, severity, exit statuses, alerting, incident flow
- `02_TRD.md` §63, §78–§88, §158–§164 — observability, async, caching, health, auditability
- `15_DEPLOYMENT.md` §8, §12 — health checks, deploy-time watchlist
- `07_API_CONTRACT.md` §7.17, §9 — health response, error envelope
- `10_SECURITY.md` — security monitoring, secret hygiene
- `13_TESTING.md` — error-path test requirements
- `MASTER_PROJECT_PROMPT.md` §63–§66, §109–§113 — observability, logging, auditability, versioning

---

# END OF MONITORING & OBSERVABILITY SPECIFICATION