# Changelog

All notable changes to SafeRoute AI are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- **Master specification** `MASTER_PROJECT_PROMPT.md` — highest-level engineering specification for SafeRoute AI (system behavior, architecture, providers, security, testing, deployment, real-world operation, absolute rules).
- **Product / Requirements docs** (`brain/01_PRD.md`, `brain/02_TRD.md`) — product requirements, technical requirements, risk-engine and testing requirements, CI/git rules.
- **Architecture** (`brain/03_ARCHITECTURE.md`) — authoritative build directive: fixed stack, repository layout, module specs, API contract, build order, verification commands, definition of done.
- **Data model** (`brain/04_DATA_MODEL.md`) — entity specs, ERD, status enums, model/dataset versioning, traceability guarantees, constraints.
- **Data & ML sources** (`brain/05_DATA_SOURCES.md`) — routing, imagery, facilities, YOLO dataset/model, and LLM providers (5 sections).
- **API contract** (`brain/07_API_CONTRACT.md`) — resource model, endpoint specs (`/api/v1/...`), errors, partial success, zero-vs-unavailable, idempotency, rate limiting.
- **UI spec** (`brain/08_UI_SPEC.md`) — design system, screens/components, loading/error/empty/partial/unavailable states, accessibility, frontend architecture.
- **Error handling** (`brain/09_ERROR_HANDLING.md`) — failure taxonomy, retry/fallback policy, logging/observability, error testing, incident diagnosis.
- **ML spec / risk engine / facility spec / LLM spec** — hazard detection, deterministic risk methodology, corridor facility search, and grounded explanation-layer requirements defined across `03_ARCHITECTURE.md` §6, `02_TRD.md`, and `04_DATA_MODEL.md` (dedicated numbered docs reserved per `MASTER_PROJECT_PROMPT.md` §99).
- **Security** (`brain/10_SECURITY.md`, `brain/security_handling.md`) — authoritative security specification: threat model, secrets, ML/model security, input/image/LLM security, CI/CD security, security testing.
- **Testing** (`brain/13_TESTING.md`) — test strategy, layers, unit/ML/risk/facility/API/E2E/security/error-path coverage, fixtures, verification commands.
- **Production checklist** (`brain/14_PRODUCTION_CHECKLIST.md`) — release gate matching `MASTER_PROJECT_PROMPT.md` §118, before-release and after-deploy gates.
- **Microtasks** (`brain/15_MICROTASKS.md`) — small shippable work items per phase with checkable boxes.
- **Deployment / Monitoring / Roadmap** (`brain/15_DEPLOYMENT.md`, `brain/16_MONITORING.md`, `brain/17_DEVELOPMENT_ROADMAP.md`) — environment separation, CI/CD, observability, and development roadmap.
- **AdMob** (`brain/11_ADMOB_SPEC.md`) — ad placement rules independent of routing/analysis functionality.
- **Real-world operation & limitations** (`MASTER_PROJECT_PROMPT.md` §92–§93, `brain/20_LIMITATIONS_AND_ASSUMPTIONS.md`) — imagery temporal limits, no-safety-guarantee disclaimer, data-quality constraints.
- **Decisions log** (`brain/17_DECISIONS.md`) — accepted architecture decisions (ADRs) with rationale and consequences.
- **Runbooks** (`runbooks/`) — `credential-reevocation-or-leak.md`, `database-migration-failure.md` incident procedures.
- **Project rules** `MASTER_RULES.md` — the master rulebook binding all agents and developers.

### Phase 1 — Foundation (complete)

- Backend scaffold: FastAPI app, externalized config (pydantic-settings), SQLAlchemy 2.0 ORM models (route / vision / facility / analysis / LLM domains), typed Pydantic schemas
- `GET /api/v1/health` returns 200; `POST /api/v1/route-requests` returns explicit honest `503 ROUTING_PROVIDER_ERROR` until routing provider is wired
- Backend tests (`pytest`): 4 passing, incl. lifespan/DB-init regression guard; lint/type-check gate ready
- Frontend scaffold: Vite + React + TypeScript, react-leaflet map, search form, route cards; `npm run build`, `npm test` (2 passing), `npm run lint` clean
- Docker Compose (`backend`, `PostgreSQL 16`, `frontend` nginx): full stack verified — health 200 via backend, frontend, and frontend→backend proxy (Phase 1 DoD pass)
- `.env.example` placeholders committed; `.env` gitignored; CI workflow (`.github/workflows/ci.yml`)

### In progress

- Phase 2 — Routing: OSRM provider adapter, route normalization, dynamic 1–4 candidate routes; Alembic migration scaffold
- Risk engine: deterministic score, configurable weights, documented formula (not yet finalized) `[DECISION REQUIRED]`
- Facilities: Overpass corridor search, category aggregation, zero-vs-unavailable handling
- LLM: grounded explanation layer with deterministic fallback when key absent

### Planned

- YOLO11 training pipeline and dataset scaffold; production model artifact
- Road image pipeline (collection, validation, OpenCV preprocessing)
- Hazard aggregation with duplicate suppression and spatial clustering
- Production hardening: caching, structured logging, rate limiting, security pass, performance tuning, full E2E suite

<!-- Keep a Changelog: use Added / Changed / Deprecated / Removed / Fixed / Security per release. Versioned after first release. -->