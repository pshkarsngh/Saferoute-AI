# 15_DEPLOYMENT.md — SafeRoute AI Deployment Specification

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Authoritative Deployment Specification
**Version:** 1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_RULES.md` > `01_PRD.md` > `02_TRD.md` > `03_ARCHITECTURE.md` > this document
**Companion:** `12_GITHUB_ACTIONS.md` (pipeline definition), `14_PRODUCTION_CHECKLIST.md` (release gate), `09_ERROR_HANDLING.md` (health/degraded behavior), `10_SECURITY.md`, `runbooks/` (incident procedures)

Any unresolved deployment decision in this document is marked `[DECISION REQUIRED]` with the missing decision, why it matters, options, and affected documents.

---

## 1. PURPOSE

This document defines how SafeRoute AI is built, packaged, promoted across environments, and operated in production. It covers:

- Deployment architecture (what runs where, what is external)
- Environment separation (development / staging / production)
- Docker Compose topology
- Containerization rules
- CI/CD pipeline
- Database migrations
- Secrets management during deployment
- Health / readiness checks
- Backups and restore
- Rollback strategy (application, model, risk engine)
- Deployment documentation requirements

It does **not** define error-handling semantics (see `09_ERROR_HANDLING.md`), monitoring/alerting (see `16_MONITORING.md`), or project testing strategy (see `13_TESTING.md`).

---

## 2. DEPLOYMENT ARCHITECTURE

The initial production deployment is a modest topology with no Kubernetes, message queue, or separate microservices unless a demonstrated requirement appears (`03_ARCHITECTURE.md` §2, `02_TRD.md` §123, `MASTER_RULES.md` §27).

```
USER
  ↓
FRONTEND (React + Vite + TypeScript static build)
  ↓ HTTPS
BACKEND (FastAPI, stateless, Python 3.11+)
  ├────────────┐
  ↓            ↓
DATABASE     CACHE (optional, in-memory/Redis only if scale justifies it)
  ↓
OPTIONAL ML WORKER (YOLO11 inference; initially inside backend per `02_TRD.md` §124)
  ↓
EXTERNAL PROVIDERS:
  Routing Provider (OSRM)
  Road Imagery Provider
  Facility Provider (Overpass)
  LLM Provider (OpenAI-compatible)
```

**Fixed decisions:**
- Frontend serves static assets via the hosting layer (or the backend as a static host in a simple Compose topology); it is never a provider-facing service.
- Backend is stateless and horizontally scalable without sticky state; all persistent state lives in PostgreSQL.
- YOLO11 inference **may** run inside the backend to begin with. A separate ML worker is introduced only when CPU/GPU or latency requirements justify it (`02_TRD.md` §124, `MASTER_PROJECT_PROMPT.md` §105). If a worker is introduced, its position is: API → job queue → ML worker → YOLO11 → result database.
- External providers are reached only through backend provider adapters (`02_TRD.md` §93–§95, `05_DATA_SOURCES.md`). The frontend never talks to providers directly (`MASTER_PROJECT_PROMPT.md` §42).
- No microservices, no Kubernetes, no message queue in v1.

---

## 3. ENVIRONMENTS

Three separated environments MUST exist (`MASTER_PROJECT_PROMPT.md` §81, `02_TRD.md` §73):

| Aspect            | development                      | staging                                | production                               |
|-------------------|----------------------------------|----------------------------------------|------------------------------------------|
| Purpose           | Local feature work               | Pre-release validation                  | Real users / real data                   |
| Database          | Local PostgreSQL (fresh/short-lived) | Production-like schema + anonymized sample data | Real schema + real data                  |
| Providers         | Mocks or keyless/test providers  | Test keys + test providers/models       | Real providers + real keys               |
| Models            | Small/local YOLO artifact, dev config | Validated staging model version     | Approved, release-pinned model version   |
| Secrets           | Development-only `.env`          | Staging-only secrets                    | Production secrets (secrets manager)     |
| Data               | Sample/demo, clearly marked `MOCK`/`TEST` | Synthetic/anonymized; never real PII | Real data; strict retention policies     |
| Access            | Developer machines                | CI/CD + QA + release approvers          | Locked-down, minimal, audited            |

**Hard rules:**
- Production secrets are **never** used in development (`MASTER_PROJECT_PROMPT.md` §81). Each environment resolves secrets from its own source.
- Development uses test models and test/mock providers; the mock boundary is always explicit and never silently reaches staging/production (`02_TRD.md` §149–§150).
- Configuration is externalized and environment-specific (`02_TRD.md` §72). Values are read at startup via `pydantic-settings`; there are no per-environment code branches.
- The `APP_ENV` variable distinguishes environments. Invalid or missing `APP_ENV` fails fast at startup (`09_ERROR_HANDLING.md` §5-U).
- Environment promotion is one-directional: development → staging → production. Skipping staging requires an explicit, documented release exception.

---

## 4. DOCKER COMPOSE TOPOLOGY

Docker Compose is the v1 containerization for reproducible environments (`02_TRD.md` §124, `03_ARCHITECTURE.md` §2). Services:

| Service   | Image base             | Role                                                            |
|-----------|------------------------|-----------------------------------------------------------------|
| `backend` | slim, minimal Python   | FastAPI app; runs HTTP API; hosts YOLO inference in v1          |
| `db`      | `postgres:16`          | PostgreSQL 16; versioned via Alembic migrations                 |
| `frontend`| node build → static    | **Optional** static host of the built React app (dev/demo only) |

**Compose rules:**
- `db` is a named volume-backed PostgreSQL 16 container; data survives restarts.
- `backend` depends on `db` health (readiness, not just start) before starting.
- The same `docker-compose.yml` shape is used across environments; environment-specific values come from per-environment `.env`/secrets, never from different compose files with baked-in credentials.
- Ports are not blindly published in production; only what the load balancer / CI health checks need.
- Logs go to stdout/stderr via structured JSON (see `16_MONITORING.md` §4); the container writes no secrets to disk.

Typically: `docker compose up db backend` in staging/prod; `docker compose up` (with `frontend`, mock providers) in development.

---

## 5. CONTAINERIZATION RULES

Every image built from this repo MUST satisfy:

1. **Non-root runtime.** Containers run as an unprivileged user (e.g., `UID 10001`). No root execution; no capability escalation.
2. **Minimal base.** Distroless/slim images only. No compilers, no dev tooling, no shell in production images where feasible.
3. **No baked secrets.** No `ARG`-injected secrets into image layers; no `.env` copied into an image. Secrets are injected only at runtime from the environment/secrets manager (`02_TRD.md` §74).
4. **Dependency hygiene.** Dependencies installed from locked manifests; versions pinned. No `latest` floating tags in production images.
5. **No model baking** unless required for offline operation — and then the model artifact plus its hash + version are recorded (see §10). By default the model is mounted/attached at deploy time from a versioned artifact store.
6. **Health endpoints present.** The image must expose `GET /api/v1/health` (see §8).
7. **Image scan.** Every image is scanned in CI (dependency vulnerabilities, known CVEs) before it can be promoted (`12_GITHUB_ACTIONS.md`).
8. **Immutable tags.** Deployments reference immutable image digests/tags that map to a specific release, which makes rollback deterministic (§11).
9. **Deterministic builds.** Multi-stage builds lock toolchains; repeated builds of the same source produce equivalent artifacts.

---

## 6. CI/CD PIPELINE

Defined in `12_GITHUB_ACTIONS.md` and executed on push/PR and on merge to the release branch. A deployment MUST NOT proceed if any critical step fails (`MASTER_PROJECT_PROMPT.md` §82).

```
1. Install dependencies (locked)
2. Lint                       — ruff (backend), eslint (frontend)
3. Type-check                 — mypy (backend), tsc (frontend)
4. Unit tests                 — pytest (backend), Vitest/RTL (frontend)
5. Integration tests          — mocked providers; DB-backed where required
6. Security scan              — dependency audit + image scan + secret scan (forbidden patterns)
7. Build                      — backend image, frontend static build
8. Migration dry-run (staging) — `alembic upgrade head` against a staging DB clone
9. Deploy (staging first)     — promote artifacts to staging
10. Health check              — POST-deploy verification of /api/v1/health + smoke endpoints
11. Deploy to production      — only after staging passes and (if configured) approval gate
12. Post-deploy verification  — health, watch metrics per `16_MONITORING.md`
13. Rollback path on failure  — previous release artifact (see §11)
```

**Pipeline rules:**
- Every stage runs in a clean, reproducible environment.
- CI secrets are masked: stored as CI platform secrets, referenced by name in the workflow, never printed, never written to logs or the workflow file (`12_GITHUB_ACTIONS.md`).
- Migration runs as an explicit, audited step before the API deploy — never as a background side effect of app startup in production.
- The build artifact used in staging is the same artifact promoted to production (no rebuild between environments).
- If a deploy health check fails, the pipeline does not proceed to the next environment; rollback is initiated (§11).

---

## 7. DATABASE MIGRATIONS

Schema changes are versioned, reviewable, repeatable, and rollback-aware (`MASTER_PROJECT_PROMPT.md` §86, `02_TRD.md` §129).

- **Tool:** Alembic with SQLAlchemy 2.0 metadata as the source of truth (`03_ARCHITECTURE.md` §2).
- **Versioned:** every change is a numbered migration file committed with its change; the DB schema version is tracked (`model/risk/API/database all versioned` — see `MASTER_RULES.md` and `04_DATA_MODEL.md`).
- **Dry-run in staging:** every migration is executed against a staging DB (production-like data/anonymized sample) before production; failures there block production deploys.
- **Reversible:** migrations define `upgrade()` and `downgrade()` where feasible. Dangerous, irreversible changes (e.g., data drops) must be explicitly documented and gated.
- **Manual production modification is forbidden** except in catastrophic recovery, and then it must be recorded and reconciled with the migration history.
- **Sequencing:** run `alembic upgrade head` as a distinct deploy phase before the new backend ships; do not couple schema application to app startup.
- **Failure:** if a migration fails mid-deploy, do not partially run the app against a half-migrated schema. Follow `runbooks/database-migration-failure.md`.
- Each migration is tied to a release and reviewed like code; the migration version is part of the compatibility matrix (frontend/backend/schema/model/risk-config, `02_TRD.md` §164).

---

## 8. HEALTH / READINESS CHECKS

The application exposes a health endpoint at `GET /api/v1/health` (`09_ERROR_HANDLING.md` §14), aligned with the API contract `07_API_CONTRACT.md` §7.17 and `02_TRD.md` §158.

Behavior:

```json
{
  "status": "healthy",
  "components": {
    "database": "healthy",
    "model": "loaded",
    "providers": "not_checked"
  },
  "version": "1.0.0"
}
```

Rules:
- The health endpoint reports component availability **without exposing internals**: no credentials, no connection strings, no internal URLs, no stack traces (`09_ERROR_HANDLING.md` §4.11). `providers` checks are separated from the basic health checks so the health probe itself does not make unplanned provider calls (`02_TRD.md` §158).
- `status: healthy` only when the service can serve requests (DB reachable; model loaded/authoritative where required for analysis).
- A degraded-but-alive service reports the failing component while keeping the process up (model load failure → `model: "unavailable"`, not a crash loop — `09_ERROR_HANDLING.md` §5-K-N).
- **Liveness** (`GET /api/v1/health`) distinguishes a running process from a ready one; **readiness** additionally verifies required dependencies (DB, model) before routing traffic to the instance.
- Orchestrators/CI and the load balancer use these checks; alerting thresholds are defined in `16_MONITORING.md` §8.

---

## 9. SECRETS MANAGEMENT IN DEPLOY

Secrets are never committed, never baked, never logged (`MASTER_RULES.md` §21, `02_TRD.md` §74, `10_SECURITY.md`).

- **Source of truth:** per-environment secrets manager (or equivalent platform secrets) in staging/production; local `.env` (gitignored) in development only.
- **Injection:** secrets are injected at runtime as environment variables into the running container/process. `.env.example` is committed with placeholders only (`03_ARCHITECTURE.md` §2).
- **CI masking:** all CI secrets are stored as masked CI platform secrets; workflows reference them by name; any accidental printed secret triggers the workflow failure + secret-revocation runbook (`runbooks/credential-reevocation-or-leak.md`).
- **Least privilege:** each component receives only the credentials it needs. The frontend and its build manifest contain **no** secrets (`MASTER_PROJECT_PROMPT.md` §45).
- **Rotation/reuse:** reuse across environments is forbidden; production secrets differ from staging. Rotation is a documented, isolated operation.
- **Detection:** a secret/pattern scan runs in CI and blocks merges (API keys, tokens, DB URLs, JWT secrets).

---

## 10. BACKUPS

Per `02_TRD.md` §161–§162 and `MASTER_PROJECT_PROMPT.md` §110.

| Artifact                    | Policy                                                                    |
|-----------------------------|---------------------------------------------------------------------------|
| Database                    | Encrypted backups at a defined frequency; retention; tested restore procedure. Restore is rehearsed, not assumed. |
| Model artifact              | Every approved artifact stored versioned (name, version, dataset version, training config, file hash). The exact production model is recoverable/copyable. |
| Configuration               | Non-secret config (route limits, search radius, risk weights, thresholds, provider base URLs, version pins) versioned in the repo; secrets excluded. |
| Structured analysis log / audit trail | Preserved per `16_MONITORING.md` §10 for reproducibility. |

**Restore procedure (must be documented per environment):**
1. Provision/verify an empty target database of the same major version (PostgreSQL 16).
2. Restore the encrypted backup; verify integrity with checksums.
3. Run `alembic` to the exact schema version recorded with the backup, or restore backups that already carry schema history.
4. Verify readiness: run `GET /api/v1/health`, spot-check a real route analysis, confirm `model_version`/`risk_engine_version` match the artifacts pinned for that release.
5. Record the restore in the audit trail.

Backup frequency, retention, and the restore runbook are recorded in the deployment documentation (see §13).

---

## 11. ROLLBACK

Rollback is a designed-in, testable path for application, model, and risk configuration (`MASTER_PROJECT_PROMPT.md` §111–§112, §14 of `14_PRODUCTION_CHECKLIST.md`).

### 11.1 Application / release rollback
- Deployments are immutable artifacts. Rollback = re-deploy the previous release image/tag.
- Triggered when the post-deploy health check fails, error rate spikes, or a release defect is confirmed (`16_MONITORING.md` §8).
- A rollback is a normal, pre-rehearsed operation: previous artifact → health check → metrics watch. No source-level undo in production.

### 11.2 Database rollback
- If a release includes a migration, a DB rollback means executing the corresponding `downgrade()` in the migration history where defined.
- If the migration is irreversible, the recovery path is backup restore (§10) — hence backups are taken before any migration-bearing release.
- Migration failures during deploy follow `runbooks/database-migration-failure.md`.

### 11.3 Model rollback (v2 → v1)
- New YOLO model (v2) performs poorly or degrades detection → switch the pinned `MODEL_VERSION`/model artifact back to v1, then re-verify. Versioning makes this a config/artifact change, never a code rewrite (`MASTER_RULES.md` §25, `MASTER_PROJECT_PROMPT.md` §111).
- Any analysis produced under v2 stays tagged `model_version=v2`; it is not silently re-attributed to v1 (`02_TRD.md` §16).

### 11.4 Risk engine versioning
- Risk calculations are versioned (`risk_engine_version`), so weight/threshold changes are traceable changes (`MASTER_PROJECT_PROMPT.md` §112, `02_TRD.md` §164).
- Rollback of a risk change = re-pin the previous risk configuration version. Historical results remain tagged with the version that produced them.

**Rollback completion requires:** health green, no metric anomaly (per `16_MONITORING.md` §8), and an incident/decision record in `16_CHANGELOG.md`.

---

## 12. MONITORING AND ALERTING DURING DEPLOY

Deployment is not finished when the container is up; it is finished when the metrics confirm health (`14_PRODUCTION_CHECKLIST.md` "After Deploy").

The post-deploy watchlist (full definitions in `16_MONITORING.md` §2):
- no 5xx spike; error rate by code within baseline
- health/readiness green on all instances
- provider success/failure ratios steady (no new RFC-issue from the deploy)
- YOLO inference latency/count normal; no model-load regression
- partial-analysis ratio not trending up
- queue latency (if a worker exists) within tolerance

---

## 13. DEPLOYMENT DOCUMENTATION REQUIREMENTS

The repository must carry deployment docs covering (`02_TRD.md` §157):

- Requirements (Python 3.11+, Node, Docker, PostgreSQL 16) and versions
- Environment variables: full externalized list with placeholders (`.env.example`), marking which are secrets
- Database setup: user, URL shape, migrations (`alembic upgrade head`), initial state
- Model setup: obtaining/validating the pinned model artifact, `MODEL_PATH`/`MODEL_VERSION`
- Backend setup: install, config checks, run (`uvicorn`), health verification
- Frontend setup: install, build (`npm run build`), static hosting
- Build: Docker build commands, immutable tags, image scan results
- Run: Compose topology, ports, volumes, logging sink
- Testing: how to run pytest / Vitest / lint / mypy / type-check
- Deployment: per-environment promotion steps, migration dry-run, health checks, rollback, backups, restore, and the post-deploy checklist
- Runbooks referenced: `runbooks/database-migration-failure.md`, `runbooks/credential-reevocation-or-leak.md`, plus `14_PRODUCTION_CHECKLIST.md`

Documentation updates are part of Definition of Done for any release that changes deployment behavior (`MASTER_RULES.md` §43, `02_TRD.md` §170).

---

## 14. RELATED DOCUMENTS

- `12_GITHUB_ACTIONS.md` — pipeline definition (CI / deploy / scrape conventions)
- `14_PRODUCTION_CHECKLIST.md` — release gate, before/after deploy verification
- `02_TRD.md` §123–§126 (deployment/containerization/env/CI), §157–§158, §161–§164
- `03_ARCHITECTURE.md` §2 (fixed stack), §11 (build order), §13 (Definition of Done)
- `09_ERROR_HANDLING.md` §12–§16 (health, monitoring, incident diagnosis)
- `16_MONITORING.md` — metrics, logging, alerting thresholds
- `MASTER_PROJECT_PROMPT.md` §80–§86, §105, §109–§112 (deployment, env, CI, health, backups, rollbacks)
- `runbooks/database-migration-failure.md`, `runbooks/credential-reevocation-or-leak.md`

---

# END OF DEPLOYMENT SPECIFICATION