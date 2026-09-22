# 14_PRODUCTION_CHECKLIST.md — SafeRoute AI Production Release Checklist

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Production Release Checklist / Release Gate
**Version:** 1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_PROJECT_PROMPT.md` §118 (final production checklist) > `03_ARCHITECTURE.md` §13 (definition of done)
**Companion:** `02_TRD.md` §126–§128 (CI/version control), `09_ERROR_HANDLING.md` (failure behavior), `10_SECURITY.md` / `security_handling.md` (security), `16_CHANGELOG.md` (release notes), `runbooks/` (incident procedures)

The system MUST NOT be called production-ready until every applicable item below is checked. This file mirrors the release gate in `MASTER_PROJECT_PROMPT.md` §118 and the per-phase Definition of Done in `03_ARCHITECTURE.md`.

> Each section below is a **release gate**. Additionally, tracked build-state checkboxes (marked `[✓]`/`[☐]`) are maintained in `17_DEVELOPMENT_ROADMAP.md` and `15_MICROTASKS.md`. This file stays authoritative for the FINAL gate; the per-phase DoD lives in `03_ARCHITECTURE.md` §11.

---

## Current Build Status (Phase 1 — Foundation, in progress)

Recorded from the working tree on 2026-09. This section is updated as phases complete; it is **informational only** — the gates below still drive release.

- [✓] Backend repository layout created (`backend/app`: `config.py`, `db.py`, `main.py`, `models/`, `schemas/`, `api/`)
- [✓] `from app.main import create_app` imports; `create_app()` boots successfully (verified via `python -c` boot check)
- [✓] Configuration externalized via pydantic-settings (`.env` overrides; never committed secrets) — `backend/app/config.py`
- [✓] SQLAlchemy 2.0 ORM models materialized for the core data model (`04_DATA_MODEL.md`): `route_requests`, `routes`, `route_segments`, `road_images`, `hazard_detections`, `hazards`, `facilities`, `route_facilities`, `risk_analysis`, `route_analysis`, `analysis_jobs`, `model_versions`, `dataset_versions`, `llm_requests`, `llm_responses`, `audit_logs`
- [✓] Pydantic schemas mirror `07_API_CONTRACT.md` (snake_case, strict `extra=forbid`)
- [✓] `GET /api/v1/health` endpoint present (liveness, no internals leaked)
- [✓] `POST /api/v1/route-requests` returns explicit `503 ROUTING_PROVIDER_ERROR` until a provider is wired — **honest unavailable, never fabricated routes** (`09_ERROR_HANDLING.md` §10.1)
- [✓] API modularized: `api/router.py` → `api/routes/{health, route_requests}.py`
- [☐] Routing provider (OSRM) integration + normalization (`03_ARCHITECTURE.md` §11 Phase 2) — **next**
- [☐] Risk engine, facility engine, LLM service, hazard aggregation wired to routes
- [☐] Frontend scaffold (Vite + React + TS + react-leaflet)
- [☐] Docker Compose, `docker-compose.yml`, Alembic migrations, `Dockerfile`s
- [☐] CI workflow (`12_GITHUB_ACTIONS.md`) + `requirements.txt` lockfile + lint/test gates
- [☐] `ml/dataset` scaffold + `data.yaml` (`06_AI_SOURCES.md`)

---

## Product

- [ ] Source and destination input works
- [ ] Candidate routes are generated (up to 4, dynamic; never padded)
- [ ] Route selection works
- [ ] Route map renders all returned routes and distinguishes them without relying on color alone
- [ ] Route cards show verified distance, duration, risk, hazards, and facility counts
- [ ] Route detail page shows map, hazards, risk, facilities, and AI explanation
- [ ] Frontend states handled: loading / error / empty / partial / unavailable (`08_UI_SPEC.md` §14)
- [ ] Zero vs unavailable is visually and textually distinct (`MASTER_PROJECT_PROMPT.md` §26)
- [ ] No "completely safe" or guaranteed-safety claims anywhere in the UI (`MASTER_PROJECT_PROMPT.md` §21)

## Computer Vision

- [ ] Road image pipeline works end-to-end (collection → validation → metadata)
- [ ] OpenCV preprocessing works (load, validate, resize, normalize, color, quality checks)
- [ ] YOLO11 works with a real trained model artifact (no fake detections)
- [ ] Model versioning exists (`model_name`, `model_version`, `dataset_version`) (`04_DATA_MODEL.md` §7.13)
- [ ] Detections are traceable to route/segment/image `model_version` provenance (`02_TRD.md` §132)
- [ ] Dataset documented: source, license, classes, split, preprocessing, version (`02_TRD.md` §55/§154)
- [ ] Confidence threshold is configurable and documented; low-confidence detections dropped consistently
- [ ] Model failure degrades to `safety.status=unavailable`, never fabricated detections (`09_ERROR_HANDLING.md` §10.4)

## Safety

- [ ] Hazard aggregation works with duplicate suppression (overlapping images not double-counted) (`MASTER_RULES.md` §12)
- [ ] Risk formula documented with weights, severity, confidence, exposure, and normalization (`02_TRD.md` §155)
- [ ] Risk score is deterministic and reproducible from inputs + config + model output (`02_TRD.md` §33)
- [ ] Risk engine versioned; historical results traceable (`MASTER_PROJECT_PROMPT.md` §112)
- [ ] No guaranteed-safety claims; score NOT presented as an official road-safety standard (`MASTER_RULES.md` §13)
- [ ] Low risk score never presented as "completely safe" (`02_TRD.md` §138)
- [ ] Missing data → risk `unavailable`, never `score=0` (`09_ERROR_HANDLING.md` §10.6)

## Facilities

- [ ] Facility search works within the configured route corridor (not the whole city) (`MASTER_PROJECT_PROMPT.md` §23)
- [ ] Categories separated: Emergency Accessibility vs Travel Convenience; never merged into a safety score (`MASTER_RULES.md` §14, `03_ARCHITECTURE.md` §6.9)
- [ ] Counts + nearest distance per category returned and displayed
- [ ] Zero results vs provider unavailable distinguished in API and UI (`02_TRD.md` §137)
- [ ] Facility deduplication works (provider ID preferred) (`02_TRD.md` §39)
- [ ] No fabricated facility names/phones/addresses/opening status (`MASTER_PROJECT_PROMPT.md` §24)
- [ ] Facility failure → `status=unavailable`; route + safety preserved (`09_ERROR_HANDLING.md` §10.7)

## AI / LLM

- [ ] LLM receives only the verified structured Route Profile (`03_ARCHITECTURE.md` §6.11)
- [ ] LLM is explanation-only: never invents hazards/facilities/routes/scores (`MASTER_PROJECT_PROMPT.md` §35)
- [ ] No hallucinated data; grounding rules enforced and tested
- [ ] LLM output validated before returning; unsupported numerical claims flagged (`02_TRD.md` §48)
- [ ] Prompt injection considered; untrusted external text cannot redefine system instructions (`MASTER_PROJECT_PROMPT.md` §47)
- [ ] LLM failure → deterministic fallback sentence; structured analysis intact (`09_ERROR_HANDLING.md` §10.8)
- [ ] LLM traceability: provider, model, prompt version, input data version, timestamp (`02_TRD.md` §113)

## Security

- [ ] Secrets protected: `.env` only, never committed, never in frontend bundle, logs, or errors (`MASTER_RULES.md` §21)
- [ ] Authentication implemented where required (v1: see ADR-001 in `17_DECISIONS.md`; rate-limited public otherwise)
- [ ] Authorization implemented for protected/admin endpoints
- [ ] Rate limiting on expensive operations (route generation, analysis, image upload, LLM) (`MASTER_PROJECT_PROMPT.md` §107)
- [ ] Input validation for coordinates, enums, payload size, route IDs (`02_TRD.md` §57)
- [ ] Upload security: MIME/extension/size/dimension/content validation (`02_TRD.md` §76)
- [ ] XSS protection: untrusted text rendered safely; malicious facility/LLM strings inert (`security_handling.md` §21)
- [ ] SQL injection protection: parameterized queries throughout
- [ ] Prompt injection defenses in place (system prompt isolation, input sanitation)
- [ ] Secure headers configured (CSP, HSTS, etc.); CORS restricted (`security_handling.md` §19)
- [ ] Dependency/secret scanning in CI; lockfiles present (`security_handling.md` §18/§21)

## Performance

- [ ] API optimized: route generation, analysis, facility, LLM calls batched/cached where justified
- [ ] Map optimized: lazy loading, marker clustering, route geometry not re-fetched unnecessarily
- [ ] ML inference optimized: model loaded once, images resized, batching where appropriate (`02_TRD.md` §91)
- [ ] Caching considered with version/config-aware keys and invalidation (`02_TRD.md` §85–§86)
- [ ] Async processing implemented where needed (analysis job) without unnecessary queue infrastructure (`02_TRD.md` §82)
- [ ] Database indexes and geospatial indexing verified (`02_TRD.md` §70)
- [ ] Resource limits configured (max routes, images, image size, facility results, timeout) (`02_TRD.md` §89)

## Reliability

- [ ] Partial failures supported: one subsystem failure never destroys the full result (`09_ERROR_HANDLING.md` §10)
- [ ] Provider failures handled (routing/facility/LLM) with isolation and no fabrication
- [ ] Timeouts enforced on every external call (`REQUEST_TIMEOUT`) (`02_TRD.md` §98)
- [ ] Retry policies implemented (bounded, exponential backoff, idempotency-safe) (`09_ERROR_HANDLING.md` §11)
- [ ] Monitoring exists (metrics + alerts) for latency, error rate, and per-stage failures (`09_ERROR_HANDLING.md` §14)
- [ ] Health endpoint (`GET /api/v1/health`, `07_API_CONTRACT.md` §7.17) reports component availability without internals
- [ ] Structured logging with `request_id` correlation; never logs secrets (`MASTER_RULES.md` §32)
- [ ] Database transactions protect multi-record writes (no half-routes) (`02_TRD.md` §71)

## Deployment

- [ ] Development environment reproducible (Docker Compose backend + db, frontend optional) (`03_ARCHITECTURE.md` §2)
- [ ] Staging environment exists and mirrors production configuration (non-prod providers/models)
- [ ] Production environment configured; secrets in secrets manager
- [ ] CI/CD pipeline: lint → tests → build → security checks → deploy on merge (`02_TRD.md` §126)
- [ ] Database migrations versioned and applied via migration process (Alembic) (`02_TRD.md` §129)
- [ ] Backups configured (database, model artifact, configuration without secrets) (`02_TRD.md` §161)
- [ ] Rollback strategy defined (previous release artifact + steps) (`MASTER_PROJECT_PROMPT.md` §110–§111)
- [ ] Provider terms, licensing, and imagery/AdMob usage verified (`MASTER_PROJECT_PROMPT.md` §89–§91)

## Documentation

- [ ] Architecture documented (`03_ARCHITECTURE.md`)
- [ ] API contract documented (`07_API_CONTRACT.md`)
- [ ] Data model documented (`04_DATA_MODEL.md`)
- [ ] ML / model + dataset documented (`05_DATA_SOURCES.md`, `02_TRD.md` §154)
- [ ] Risk engine documented (formula, weights, normalization, limitations) (`02_TRD.md` §155)
- [ ] Security documented (`security_handling.md`)
- [ ] Testing documented and green (`13_TESTING.md`)
- [ ] Deployment documented (`15_DEPLOYMENT.md`)
- [ ] Monitoring documented (`16_MONITORING.md`)
- [ ] Real-world operation and limitations documented (temporal imagery limits, no safety guarantee) (`MASTER_PROJECT_PROMPT.md` §92–§93)
- [ ] Runbooks accessible to operators (`runbooks/`)

---

## Before Release

- [ ] CI green end-to-end (back: `ruff check .`, `mypy app`, `pytest -q`; front: `npm run lint`, `npm test`, `npm run build`) (`03_ARCHITECTURE.md` §12)
- [ ] Migrations tested on a production-like dataset; rollback of each migration verified
- [ ] Secrets configured in the secrets manager / `.env` for the target environment; never in repo
- [ ] AdMob unit IDs swapped from test to production IDs (`18_ADMOB_SPEC.md`); placement rules validated
- [ ] Model artifact checksummed and versioned; `MODEL_PATH`/`MODEL_VERSION`/`DATASET_VERSION` pinned and documented (`02_TRD.md` §162)
- [ ] Risk configuration (weights, severity, exposure, normalization) documented and versioned; deterministic tests pass (`02_TRD.md` §155)
- [ ] License/DECISION REQUIRED review complete: imagery provider, YOLO11/license, dataset license, facility provider terms, LLM provider terms (`MASTER_PROJECT_PROMPT.md` §90–§91). Unresolved items recorded as `[DECISION REQUIRED]`.
- [ ] Changelog updated (`16_CHANGELOG.md`) with the release's Added/Changed/Fixed
- [ ] Rollback plan defined: previous release artifact, revert steps for migrations/config/model, tested runbook
- [ ] Monitoring/alerts configured for the release; threshold baselines known
- [ ] Rate limits and abuse-prevention tuned for expected traffic (`MASTER_PROJECT_PROMPT.md` §107–§108)

---

## After Deploy

- [ ] Health checks pass; `/api/v1/health` reports healthy components
- [ ] No 5xx spike; error rate within baseline (`09_ERROR_HANDLING.md` §14)
- [ ] Latency within targets for route generation, analysis (async), facility, and LLM stages; no sustained increase
- [ ] Route + analysis smoke test succeeds against production (real providers, real small route); no fabricated values
- [ ] Monitoring noise-free: alert thresholds not spamming; no false positives
- [ ] Runbooks accessible to the on-call team; operators know the incident diagnosis flow (`09_ERROR_HANDLING.md` §16)
- [ ] Backups confirmed running; rollback artifact confirmed available
- [ ] Structured logs verified: `request_id` correlation present, no secrets logged (`MASTER_RULES.md` §32)
- [ ] Release marked in `16_CHANGELOG.md` with a version tag; tag matches deployment artifact

---

## Related

- `MASTER_PROJECT_PROMPT.md` §118 — the authoritative final production checklist this file implements
- `03_ARCHITECTURE.md` §12 (verification commands), §13 (definition of done)
- `02_TRD.md` §126–§128 (CI/CD, git requirements, branching)
- `09_ERROR_HANDLING.md` — failure behavior the release must demonstrate
- `security_handling.md` — security requirements
- `16_CHANGELOG.md` — release notes
- `runbooks/` — `database-migration-failure.md`, `credential-reevocation-or-leak.md`

---

# END OF PRODUCTION RELEASE CHECKLIST