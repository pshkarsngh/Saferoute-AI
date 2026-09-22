# 09_ERROR_HANDLING.md — SafeRoute AI Error Handling & Failure Management

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Authoritative Error-Handling / Failure-Management Specification
**Version:** 1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_RULES.md` > `01_PRD.md` > `02_TRD.md` > `03_ARCHITECTURE.md` > `04_DATA_MODEL.md` > `07_API_CONTRACT.md` > this document
**Companion:** `08_UI_SPEC.md` (frontend states), `05_DATA_SOURCES.md` (providers), `10_SECURITY.md`

Any unresolved architectural decision in this document is marked `[DECISION REQUIRED]` with the missing decision, why it matters, options, and affected documents.

---

## 1. PROJECT CONTEXT

SafeRoute AI lets a user enter a **source** and **destination**, generates up to 4 candidate routes, and analyzes each route through: road imagery → OpenCV → YOLO11 → hazard aggregation → deterministic risk → facility discovery → Route Profile → grounded LLM explanation → frontend.

**Non-negotiable boundaries this spec enforces:**

- The LLM is an explanation layer only. It never replaces routing/OpenCV/YOLO11, never calculates the risk score, never modifies verified data, never invents hazards/facilities/distances/routes, never turns missing data into zero, and never claims guaranteed safety.
- Road Safety, Emergency Accessibility, Travel Convenience, and Route Information are separate dimensions and are **never merged into one arbitrary score**.
- Hazard classes come from the actual dataset (`ml/dataset/data.yaml`); facility categories are hospital, medical_store, restaurant, hotel, petrol_pump, police_station.
- **Unavailable data is never rendered as zero**; a failed analysis is never presented as a successful one.

---

## 2. DOCUMENT AUTHORITY

This document is the authoritative source for error-handling behavior. It must remain consistent with: MASTER_RULES, PRD, TRD, Architecture, Data Model, Data Sources, API Contract, UI Spec, Security, Testing, Deployment, Monitoring.

- If a behavior needed here is not defined elsewhere, this document does **not** invent a project decision.
- Unresolved decisions are recorded as `[DECISION REQUIRED]` with: what is missing, why it matters, possible options, recommended considerations, and affected documents.
- No architecture is created here that conflicts with other documents.

---

## 3. PRIMARY OBJECTIVE

Define exactly how the system handles failure end-to-end, answering: what can fail, where, how detected, how classified, recoverable?, retry policy (count, stop conditions), fallback behavior, partial-result rules, frontend behavior, backend logs, what the user sees, what is never exposed, provider/YOLO/OpenCV/facility/LLM/database/timeout/input failure behavior, partial-route behavior, cross-service correlation, error testing, and production diagnosis.

---

## 4. CORE ERROR-HANDLING PRINCIPLES

1. Never hide errors.
2. Never fabricate data to make the UI look complete.
3. Never convert unavailable data into zero.
4. Never treat a failed analysis as a successful analysis.
5. Never claim a route is safe because analysis failed.
6. Never let one optional subsystem failure unnecessarily destroy the entire result.
7. Preserve valid partial results whenever safely possible.
8. Clearly distinguish: `zero` · `unavailable` · `not_started` · `processing` · `failed` · `partial` · `completed`.
9. User-facing messages must be understandable.
10. Internal logs carry enough technical detail for debugging.
11. Never expose stack traces, secrets, tokens, internal URLs, DB details, or sensitive infrastructure to users.
12. Errors have stable machine-readable error codes.
13. Errors are traceable via correlation/request IDs.
14. Retries are bounded.
15. Retries never create duplicate side effects (idempotency-safe).
16. External services are treated as unreliable dependencies.
17. LLM failure never destroys verified structured analysis.
18. ML failure is never silently ignored.
19. Security validation errors fail safely.
20. Error handling is consistent across frontend and backend.

---

## 5. ERROR TAXONOMY

An error has: **category / code(s) / HTTP status / severity / recoverability / retry / fallback / logging / frontend behavior / user message pattern.**

### A–E. Validation, Auth, Authorization, Request

| Category | Examples | Severity | Recoverable | Retry | Fallback | Frontend / user message |
|----------|----------|----------|-------------|-------|----------|--------------------------|
| Validation | lat out of range, malformed JSON, unknown filter | INFO | Yes (fix input) | No | No | Inline field errors: "Please enter a valid destination." |
| Request | missing required fields, bad route_id | INFO | Yes (fix input) | No | No | "Invalid request." (code shown in UI state) |
| Auth (if enabled later) | bad/missing token | INFO | Yes (re-auth) | No | No | "Please sign in to continue." |
| Authorization | forbidden resource | WARNING | Yes (user) | No | No | "You don't have access to this." |

### F–H. Routing, Provider, Network, Timeout

| Category | Examples | Severity | Recoverable | Retry | Fallback |
|----------|----------|----------|-------------|-------|----------|
| Routing | provider 5xx, provider schema change, no route found | ERROR | Transient: yes; permanent: no | Transient only, bounded | Run with remaining routes if ≥1; else clear NO_ROUTE_FOUND |
| External provider | routing/facility/LLM provider unavailable | WARNING/ERROR | Yes (transient) | Bounded backoff | Isolate the subsystem; partial result; service marked unavailable |
| Network | DNS fail, connection reset | ERROR | Yes | Bounded | Per-provider fallback adapter if configured |
| Timeout | provider/LLM exceeds `REQUEST_TIMEOUT` | ERROR | Yes | Max 1 for idempotent-safe ops | async job continues; frontend polls |

### I–J. Database, Storage

| Category | Examples | Severity | Recoverable | Retry | Fallback |
|----------|----------|----------|-------------|-------|----------|
| Database | connection loss, migration failure, constraint violation | CRITICAL/ERROR | Yes (connection pool/backoff) | Bounded; transaction safe | Return explicit DATABASE_ERROR; never fabricate results |
| Storage | image object missing, quota exceeded | ERROR | Yes | No | Mark image unavailable; skip gracefully |

DB operations must be transactional (`04_DATA_MODEL.md` §10): no dangling half-routes. A failed critical persistence step fails the request explicitly rather than returning partial phantom data.

### K–N. Image ingestion, OpenCV, YOLO, Model

| Category | Examples | Severity | Recoverable | Retry | Fallback |
|----------|----------|----------|-------------|-------|----------|
| Image ingestion | corrupted file, bad MIME, too large | WARNING | No (data-dependent) | Re-fetch once | Segment marked non-analyzed (never "no hazards") |
| OpenCV | decode failure, invalid dimensions, quality gate reject | WARNING | No | No | Image marked invalid; reason recorded (`ImageProcessingResult`) |
| YOLO inference | runtime error, bad tensor, OOM | ERROR | Yes (per-image) | 1 bounded retry | Safety → unavailable; route/facilities preserved |
| Model loading | artifact missing, corrupt, version mismatch | CRITICAL | Yes (deploy fix) | No | `YOLO status = unavailable`; system stays up |

### O–T. Model version, aggregation, risk, facilities, LLM, serialization

| Category | Examples | Severity | Recoverable | Retry | Fallback |
|----------|----------|----------|-------------|-------|----------|
| Model version | class mismatch, missing model_version_id | CRITICAL | Yes (config fix) | No | Reject detection rows that lack version provenance |
| Hazard aggregation | clustering misconfigured, overflow | ERROR | Yes (rerun) | Yes, bounded | Return partial hazard counts with `status=partial` |
| Risk engine | config error, unknown weight | ERROR | Yes (fix config) | No | Risk → unavailable; never `score=0` |
| Facility search | provider 5xx, malformed response | WARNING/ERROR | Yes (transient) | Bounded backoff | Facility status unavailable; route/safety preserved |
| LLM | provider error, timeout, invalid output | WARNING | Yes (transient) | 1 bounded retry | Deterministic fallback text; structured analysis intact |
| Serialization | provider schema mismatch, parse failure | ERROR | Yes (fix/normalize) | No | Provider-specific failure, isolated to that adapter |

### U–Z. Configuration, dependency, resource, rate-limit, security, unexpected

| Category | Examples | Severity | Recoverable | Retry | Fallback |
|----------|----------|----------|-------------|-------|----------|
| Configuration | missing env var, invalid value | CRITICAL | Yes (deploy fix) | No | Fail fast at startup where safe; health reports degraded |
| Dependency | SDK/package missing, version mismatch | CRITICAL | Yes (fix) | No | Fail fast; CI catches before deploy |
| Resource exhaustion | memory/CPU/GPU/disk | CRITICAL | Yes (scale) | No | Backpressure; 503/504; never silent |
| Rate limit | 429 from providers or on our API | INFO | Yes (wait) | Backoff + `Retry-After`; bounded | Cache results; avoid duplicate calls |
| Security | XSS payload, attempted traversal, bad upload | CRITICAL | No | No | Reject; log WARNING/ERROR; alert on pattern |
| Unexpected | unhandled exception | ERROR | No | No | 500 INTERNAL_ERROR; error boundary; monitor |

---

## 6. ERROR SEVERITY LEVELS

| Level | Meaning |
|-------|---------|
| INFO | Expected, recoverable, or informational state (e.g., low confidence dropped, 429 received) |
| WARNING | Subsystem problem that does not necessarily invalidate the entire route result (e.g., one image invalid) |
| ERROR | Operation failed; user action or system recovery may be required (e.g., risk not calculated) |
| CRITICAL | Major failure, security incident, data-corruption risk, or service-wide failure (model unloadable, DB out) |

Severity ≠ user-visible impact. A WARNING (one invalid image) can be invisible to the user, while an ERROR may still return a usable partial result. Severity drives logging/alerting; concrete `analysis.status` drives the UI.

---

## 7. ERROR LIFECYCLE

```text
Error Occurs
  → Detect
  → Classify (taxonomy §5)
  → Attach Context (request_id, route_id, stage, provider, model_version)
  → Assign Error Code (stable catalogue, §8)
  → Determine Severity (§6)
  → Determine Recoverability
  → Retry / Fallback / Partial Result / Fail
  → Log (structured, no secrets)
  → Return Safe Response (error envelope / partial status)
  → Frontend Handles State (08_UI_SPEC §14)
  → User Sees Appropriate Message
  → Monitoring / Alerting (§14)
```

---

## 8. ERROR CODE CATALOGUE

Stable, machine-readable codes (consistent with `07_API_CONTRACT.md` §9):

```
VALIDATION_ERROR          400/422
INVALID_COORDINATES       422
INVALID_REQUEST           400
INVALID_IMAGE             400
IMAGE_TOO_LARGE           413
UNAUTHORIZED              401
FORBIDDEN                 403
NOT_FOUND                 404
ROUTE_NOT_FOUND           404
NO_ROUTE_FOUND            404
ROUTING_PROVIDER_ERROR    502
IMAGE_NOT_AVAILABLE       503
IMAGE_PROCESSING_FAILED   500
OPENCV_PROCESSING_FAILED  500
YOLO_INFERENCE_FAILED     500
MODEL_LOAD_FAILED         500
MODEL_VERSION_MISMATCH    500
HAZARD_ANALYSIS_FAILED    500
RISK_CALCULATION_FAILED   500
FACILITY_PROVIDER_ERROR   502
FACILITY_UNAVAILABLE      503
LLM_PROVIDER_ERROR        502
LLM_UNAVAILABLE           503
ANALYSIS_TIMEOUT          504
DATABASE_ERROR            500
STORAGE_ERROR             500
RATE_LIMITED              429
CONFIGURATION_ERROR       500
SECURITY_VIOLATION        403
INTERNAL_ERROR            500
```

Only codes actually supported are used; adding a code requires updating this catalogue, `07_API_CONTRACT.md`, and frontend state mapping.

---

## 9. API ERROR RESPONSE CONTRACT

Every error response uses the envelope from `07_API_CONTRACT.md`:

```json
{
  "error": {
    "code": "ROUTE_NOT_FOUND",
    "message": "No route was found for the requested locations.",
    "details": null,
    "request_id": "req_123"
  }
}
```

- `details` is reserved for structured, non-sensitive context (e.g., field-level validation); never stack traces.
- HTTP status is always semantically correct (never 200 for failures).

**Partial-success responses** (not errors) use the partial envelope:

```json
{
  "analysis": { "status": "partial",
    "safety": { "status": "unavailable" },
    "facilities": { "status": "completed" } }
}
```

---

## 10. PER-SUBSYSTEM FAILURE POLICIES

### 10.1 Routing provider failure

- Detect: HTTP non-2xx / schema validation failure.
- Retry: transient only (5xx, timeout), bounded (max 3, exponential backoff + jitter).
- No retry on 4xx or invalid coordinates.
- If ≥1 route still valid → return them; set no fabrication. If all fail → `NO_ROUTE_FOUND` / `ROUTING_PROVIDER_ERROR`.
- LLM never steps in to invent routes.

### 10.2 Image ingestion failure

- Corrupt/MIME/size failures → image row `processing_status=invalid` + reason (`04_DATA_MODEL.md` §7.6). That segment is "not analyzed" — never "no hazards".

### 10.3 OpenCV failure

- Any preprocessing failure → `ImageProcessingResult.status = rejected|failed` with reason. Excluded from inference. Log `OPENCV_PROCESSING_FAILED` (WARNING).

### 10.4 YOLO11 failure

- Per-image transient error → 1 bounded retry.
- Persistent or load failure → safety stage `unavailable`. Route info + facilities still returned (`MASTER_RULES.md` §22 pattern). Log `YOLO_INFERENCE_FAILED` / `MODEL_LOAD_FAILED` (ERROR/CRITICAL) with `model_version` and `image_id`.
- Never fabricate detections when the model is down.

### 10.5 Hazard aggregation failure

- Partial clustering runs can return `status=partial` with a note. Configuration errors (`CLUSTER_RADIUS_M` invalid) are fail-fast at startup.

### 10.6 Risk-engine failure

- Deterministic, unitary, documented. If inputs missing → `risk_status=unavailable`, **never `score=0`**. Config/version mismatches are errors surfaced in `risk.status` and logs.

### 10.7 Facility failure

- Provider unavailable → facility domain `status=unavailable`; route + safety unaffected.
- Zero vs unavailable: successful search returning zero → `count: 0`; provider failure → `{ "status": "unavailable" }`. Never blur them (`08_UI_SPEC` §14.6).

### 10.8 LLM failure

- Provider error/timeout → max 1 retry, then deterministic fallback sentence built from the verified profile (`fallback: true`).
- Structured analysis (risk, hazards, facilities, route) is always returned regardless of LLM state.
- LLM output is validated (`02_TRD.md` §48) before returning; unsupported numerical claims flagged/fallback.

### 10.9 Database failure

- Connection errors → bounded backoff with connection pooling; critical persistence failure fails the request explicitly with `DATABASE_ERROR` (no phantom results).
- Migrations: see `runbooks/database-migration-failure.md`.

### 10.10 Timeouts

- Every external call gets `REQUEST_TIMEOUT` (`02_TRD.md` §98). Analysis timeout → `ANALYSIS_TIMEOUT` / 504, or async job continues and frontend polls (`GET /jobs/{job_id}`).

### 10.11 Rate limits

- Respect provider 429s, exponential backoff, `Retry-After`, caching.
- Our API: `429 RATE_LIMITED` + `Retry-After` on protected endpoints (route generation, analysis, image upload, LLM).

### 10.12 Security/malicious input

- Reject with validation/security codes; sanitize; never execute; alert on patterns. Fail closed.

---

## 11. RETRY & FALLBACK POLICY

### 11.1 Retry matrix (summary)

| Operation | Retryable? | Max | Backoff | Idempotency |
|-----------|-----------|-----|---------|-------------|
| Routing provider (5xx/timeout) | Yes | 3 | exp+jitter | Safe (read) |
| Facility provider | Yes | 3 | exp | Safe (read) |
| Image fetch | One re-fetch | 1 | fixed | Safe |
| YOLO per-image | Yes | 1 | fixed | Safe (stateless) |
| LLM call | Yes | 1 | fixed | Use `Idempotency-Key` / same analysis id |
| DB connection | Yes | bounded | exp | Transaction-scoped |
| 4xx / invalid input | No | — | — | — |
| Security violations | No | — | — | — |

- Never retry on: invalid credentials, invalid request, invalid coordinates, unsupported request, malicious input.
- Expensive POSTs honor `Idempotency-Key` so bounded retries never duplicate side effects (`07_API_CONTRACT.md` §11.7).

### 11.2 Fallback rules

- LLM → deterministic fallback text.
- YOLO → safety unavailable (no fabricated detections).
- Facility → unavailable domain.
- Routing → remaining valid routes or explicit no-route error.
- Never a fallback that fabricates or converts missing → zero.

---

## 12. LOGGING & OBSERVABILITY

### 12.1 Structured logging

- Fields: `ts, level, service, request_id, route_id, job_id, stage, duration_ms, error_code, error_type, provider, status, model_version, configuration_version`.
- Correlation: backend-generated `request_id` (or echoes `X-Request-ID`) flows through all stages and into the error envelope and frontend state.
- **Never log:** API keys, passwords, tokens, DB credentials, private coordinates beyond operational need, JWT secrets, stack traces of dependencies internal paths (log error codes + messages).

### 12.2 Classification mapping

- `DEBUG/INFO` → trace, expected states (429, dropped-low-confidence).
- `WARNING` → subsystem degradation (invalid image, provider blip).
- `ERROR` → failed operation with user/system follow-up.
- `CRITICAL` → model load failure, DB down, security incident.

### 12.3 Exit statuses

- Every outcome is one of: `succeeded | partial | failed | unavailable | cancelled | timed_out` — no silent holes.

---

## 13. FRONTEND ERROR BEHAVIOR

Mapped from `08_UI_SPEC.md` §14:

- **Validation/request:** inline field errors; understandable copy.
- **Route generation fail:** "Unable to generate routes right now." Actions: Retry, Edit locations.
- **Facility unavailable:** "Facility information is currently unavailable." (≠ zero).
- **Hazard analysis failed:** "Safety analysis could not be completed." + Retry Analysis; never show `risk: 0`.
- **YOLO/model down:** safety section shows unavailable state; route/facilities remain visible.
- **LLM fail:** show structured analysis normally; explanation area: "AI explanation is currently unavailable."
- **Partial:** per-domain status chips (Route ✓, Safety ✓, Facilities ✗, AI —); never hide the route.
- **Unexpected UI error:** app-level error boundary with Retry / Reload / Return to route.
- Error copy explains *what happened* and *next step*; never stack traces or secrets; `request_id` discoverable for support.

---

## 14. MONITORING & ALERTING

Metrics (from `02_TRD.md` §159): `route_requests_total`, `route_generation_failures`, `analysis_requests_total`, `analysis_failures`, `yolo_inference_count`, `yolo_inference_duration`, `facility_requests_total`, `facility_failures`, `llm_requests_total`, `llm_failures`, `average_analysis_duration`, plus `error_rate` by code and `partial_analysis_count`.

Alerts:
- YOLO/model load failure (CRITICAL) — paged.
- DB unavailability — paged.
- Sustained provider failure (routing/facility/LLM) above threshold — alert WARNING.
- Spike in `INTERNAL_ERROR`, `SECURITY_VIOLATION` — alert + incident runbook (`runbooks/`).
- `partial` ratio trending up — attention.

Health endpoint (`GET /api/v1/health`) reports component availability without exposing internals (`07_API_CONTRACT.md` §7.17).

---

## 15. TESTING ERROR HANDLING

Required error-path tests (mirrors `13_TESTING.md` / `02_TRD.md` §112, §108–§110):

- API: valid request, invalid request, missing fields, invalid coordinates, no route, provider failure, timeout, rate limit.
- Providers: mocked failures (routing/facility/LLM) → assert isolation + no fabrication.
- ML: model load failure, invalid image, empty detections, class mismatch, YOLO failure → safety unavailable.
- Risk: missing data → `unavailable`, boundary values, determinism; never zero-on-failure.
- Facility: provider error → `unavailable`; zero vs unavailable distinguished.
- LLM: provider error → fallback; grounding violations rejected; output validation.
- Partial: one subsystem fails → assert partial envelope + frontend states.
- Frontend: error boundary, error/empty/partial/unavailable states, keyboard + a11y.
- Security: XSS, unsafe LLM text, malicious names/URLs, traversal, oversized uploads → rejected safely.

---

## 16. PRODUCTION INCIDENT DIAGNOSIS

1. Find the `request_id` (UI support info or logs).
2. Follow correlation fields across stages.
3. Read structured log for `error_code`, `stage`, `provider`, `model_version`.
4. Distinguish app bug vs provider outage vs config/model issue from metrics + alert banners.
5. Use partial-status flags to see which domain failed and which remained valid.
6. Consult runbooks: `credential-reevocation-or-leak.md`, `database-migration-failure.md`.
7. Fix via smallest correct change; run error-path tests; update docs if behavior changed.

---

## 17. RELATED DOCUMENTS

- `07_API_CONTRACT.md` §9 (error codes/HTTP), §9.4 (partial success)
- `08_UI_SPEC.md` §14 (states), §13 (AI disclaimers)
- `02_TRD.md` §80 (classification), §82–§84 (async/job stages), §96–§98 (retry/timeout), §140–§141 (partial)
- `04_DATA_MODEL.md` (status enums, `processing_status`, `analysis_status`)
- `MASTER_RULES.md` §22 (graceful handling), §23 (no fabrication), §32 (logging)
- `10_SECURITY.md` (security validation fail-closed)
- `runbooks/` (incident procedures)

---

# END OF ERROR-HANDLING SPECIFICATION