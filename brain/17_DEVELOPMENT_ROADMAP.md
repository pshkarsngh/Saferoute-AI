# 17_DEVELOPMENT_ROADMAP.md — SafeRoute AI Development Roadmap

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Authoritative Development Roadmap
**Version:** 1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_RULES.md` > `01_PRD.md` > `02_TRD.md` > `03_ARCHITECTURE.md` > `MASTER_PROJECT_PROMPT.md` §101 > this document
**Companion:** `03_ARCHITECTURE.md` §11 (build order + DoD), `13_TESTING.md` (test plan), `15_DEPLOYMENT.md` (ship mechanics), `14_PRODUCTION_CHECKLIST.md` (release gate)

---

## 1. PURPOSE

This roadmap maps the 13-phase project plan of `MASTER_PROJECT_PROMPT.md` §101 onto the 10 build phases of `03_ARCHITECTURE.md` §11. It defines, per phase: the goal, key deliverables, definition of done, and the docs/services the phase lands in. It also records the current status and the near-term sprint milestones.

The phases must be completed in order; do not skip foundational work to build UI ("do not skip to nice-to-haves" — `03_ARCHITECTURE.md` §11, `MASTER_RULES.md` §42).

---

## 2. PHASE MAP — 13 Prompt Phases → 10 Build Phases

| # | 13-Phase plan (`MASTER_PROJECT_PROMPT.md` §101) | Build phase (`03_ARCHITECTURE.md` §11) |
|---|-------------------------------------------------|-----------------------------------------|
| 1 | Phase 1 — Requirements                             | (pre-build; feeds every phase)           |
| 2 | Phase 2 — Architecture                             | Phase 1 — Foundation                     |
| 3 | Phase 3 — Routing                                  | Phase 2 — Routing                        |
| 4 | Phase 4 — Imagery                                  | Phase 3 — Road Image Pipeline            |
| 5 | Phase 5 — OpenCV                                   | Phase 3 — Road Image Pipeline            |
| 6 | Phase 6 — YOLO11                                   | Phase 4 — YOLO11                         |
| 7 | Phase 7 — Hazard Aggregation                        | Phase 5 — Hazard Aggregation             |
| 8 | Phase 8 — Risk Engine                              | Phase 6 — Risk Engine                    |
| 9 | Phase 9 — Facilities                               | Phase 7 — Facility Intelligence          |
| 10| Phase 10 — LLM                                     | Phase 8 → Phase 9 — Route Profile + LLM  |
| 11| Phase 11 — Production Security                     | Phase 10 — Production Hardening          |
| 12| Phase 12 — Testing                                 | Phase 1–10 (continuous) + Phase 10        |
| 13| Phase 13 — Deployment                              | Phase 10 — Production Hardening          |

Requirements (Prompt Phase 1) produce the docs that exist today (`01_PRD.md` … `14_PRODUCTION_CHECKLIST.md`); every build phase must be traceable back to a requirements decision.

---

## 3. PHASE DETAILS

### Phase 1 — Foundation
**Prompt phases:** 1 (Requirements) + 2 (Architecture).
**Goal:** Reproducible scaffold: backend, frontend, database, Compose, config, CI all alive and green.
**Key deliverables:**
- Backend scaffold: FastAPI app, `pydantic-settings` config, DB engine/session, `GET /api/health`
- Frontend scaffold: Vite + React + TS + react-leaflet shell
- `docker-compose.yml` (backend, db, frontend optional), `.env.example`
- CI workflow (lint, type-check, unit tests, security scan) per `12_GITHUB_ACTIONS.md`
- Directory layout matching `03_ARCHITECTURE.md` §3
**Definition of done:**
- [ ] `GET /api/health` returns 200
- [ ] Frontend renders in dev
- [ ] Docker Compose up works (backend ↔ db)
- [ ] ruff / mypy / pytest / eslint / tsc green
- [ ] No secrets committed; `.env.example` placeholders only
**Lands in:** `backend/`, `frontend/`, `docker-compose.yml`, `.env.example`; docs `15_DEPLOYMENT.md` §3–§5 exercised.

### Phase 2 — Routing
**Prompt phase:** 3 (Routing).
**Goal:** Source + destination produce up to 4 normalized candidate routes via OSRM.
**Key deliverables:**
- `RoutingService` abstraction + OSRM provider + normalization (`03_ARCHITECTURE.md` §6.1)
- `POST /api/routes` returning `{request_id, routes[]}`; 1–4 routes, never fabricated (`MASTER_RULES.md` §6)
- Frontend draws returned route polylines with distinct styling
- Error envelope + error codes for routing failures (`09_ERROR_HANDLING.md` §8)
**Definition of done:**
- [ ] Source+destination returns up to 4 normalized routes
- [ ] Fewer-than-4 behavior demonstrated; no hard-coded A/B/C/D
- [ ] Unit tests for normalization + multi-route handling
- [ ] Provider failure handled (no fake route) per `09_ERROR_HANDLING.md` §10.1
**Lands in:** `backend/app/services/routing/`, `backend/app/api/routers.py`, `frontend/src/components/RouteMap.tsx`; contract `07_API_CONTRACT.md`.

### Phase 3 — Road Image Pipeline
**Prompt phases:** 4 (Imagery) + 5 (OpenCV).
**Goal:** Per route/segment: collect, validate, and preprocess road imagery with full metadata.
**Key deliverables:**
- Route segmentation service
- Image retrieval service + validation (MIME, size, readability, dimensions) per `02_TRD.md` §17
- OpenCV preprocessing + quality gates (`03_ARCHITECTURE.md` §6.3)
- Image metadata/corpus with `route_id`, `segment_id`, `source`, `timestamp` (`02_TRD.md` §16)
**Definition of done:**
- [ ] Images fetch/validate/preprocess per segment with metadata attached
- [ ] Invalid images marked (never "no hazards") per `09_ERROR_HANDLING.md` §10.2–10.3
- [ ] Imagery-limited UI language ("Road imagery unavailable for this section")
- [ ] OpenCV tests: validation, resize, format/conversion failures
**Lands in:** `backend/app/services/vision/`; docs `05_DATA_SOURCES.md`, `02_TRD.md` §15–§19.

### Phase 4 — YOLO11
**Prompt phase:** 6 (YOLO11).
**Goal:** Trained YOLO11 model runs inference and returns structured, versioned detections.
**Key deliverables:**
- `ml/training/train.py` + dataset scaffold (`ml/dataset` with train/val/test + `data.yaml`)
- `yolo_service.py` inference; model loaded once per process (`02_TRD.md` §91)
- Structured detections with image/route/segment/model_version tags (`03_ARCHITECTURE.md` §6.4)
- Model versioning (name, version, dataset version, threshold) per `MASTER_RULES.md` §25
- Dataset documentation: source, license, classes, split, version (`02_TRD.md` §154)
**Definition of done:**
- [ ] Running inference returns structured detections with version tags
- [ ] Class list derives from `data.yaml`; no invented classes
- [ ] Confidence threshold configurable; detections filtered by it
- [ ] Model-load failure handled (safety unavailable), no fabricated detections (`09_ERROR_HANDLING.md` §10.4)
- [ ] ML test requirements pass (`02_TRD.md` §109); dataset/licensing documented
**Lands in:** `ml/`, `backend/app/services/vision/yolo_service.py`, `04_DATA_MODEL.md`, `06_AI_SOURCES.md`.

### Phase 5 — Hazard Aggregation
**Prompt phase:** 7 (Hazard Aggregation).
**Goal:** Convert image detections into route/segment hazard summaries with duplicate suppression.
**Key deliverables:**
- Aggregation pipeline: image → segment → route (`03_ARCHITECTURE.md` §6.6)
- Dedup/clustering by geographic proximity, segment, image overlap (`02_TRD.md` §27–§28)
- Hazard summary + traceability (hazard → image → segment → route → request)
**Definition of done:**
- [ ] Aggregation unit tests; no double counting on overlapping images
- [ ] Same pothole in 5 images does not become 5 potholes
- [ ] Partial clustering failures return `status=partial` with note (`09_ERROR_HANDLING.md` §10.5)
**Lands in:** `backend/app/services/safety/hazard_aggregation.py`, `04_DATA_MODEL.md`.

### Phase 6 — Risk Engine
**Prompt phase:** 8 (Risk Engine).
**Goal:** Deterministic, documented, versioned 0–100 risk metric independent of the LLM.
**Key deliverables:**
- Configurable `hazard_weight × confidence × severity × exposure` summation (`03_ARCHITECTURE.md` §6.7)
- Normalization, boundary handling, missing-data rules (`02_TRD.md` §34)
- `risk_engine_version` tagging (`MASTER_PROJECT_PROMPT.md` §112)
- Formula/weights documented (`10_RISK_ENGINE.md`, `02_TRD.md` §155)
**Definition of done:**
- [ ] Known-input → expected-score unit tests
- [ ] Missing data → `risk_status=unavailable`, never `score=0` (`09_ERROR_HANDLING.md` §10.6)
- [ ] Deterministic (same input+config+model → same score)
- [ ] Not presented as official/universal safety standard
**Lands in:** `backend/app/services/safety/risk_engine.py`, `10_RISK_ENGINE.md`, config (`HAZARD_WEIGHTS`, versioned).

### Phase 7 — Facility Intelligence
**Prompt phase:** 9 (Facilities).
**Goal:** Corridor search via Overpass; counts + nearest per category; zero ≠ unavailable.
**Key deliverables:**
- Facility abstraction + Overpass provider (`02_TRD.md` §93), corridor search within `FACILITY_SEARCH_RADIUS_KM`
- Categories: hospital, medical_store, restaurant, hotel, petrol_pump, police_station
- Dedup (provider ID/coords/name) and route-distance calculation (`02_TRD.md` §39–§40)
- Aggregated per-route response (count + nearest distance)
**Definition of done:**
- [ ] Facilities associated to the correct route; route corridor respected
- [ ] Zero vs unavailable distinguished everywhere (`MASTER_PROJECT_PROMPT.md` §26)
- [ ] Facility tests: empty, duplicates, categories, provider failure (`02_TRD.md` §111)
**Lands in:** `backend/app/services/facilities/`, `11_FACILITY_SPEC.md`, `04_DATA_MODEL.md`.

### Phase 8 — Route Profile
**Prompt phase:** 10 (LLM — first half) + part of 2.
**Goal:** Canonical structured RouteProfile combining verified route/safety/facility info with partial-failure guards.
**Key deliverables:**
- Route profile engine merging route + hazards + risk + facilities (`03_ARCHITECTURE.md` §6.10)
- Per-domain status chips; partial envelope preserved (`09_ERROR_HANDLING.md` §9)
- Safety vs convenience never merged (`03_ARCHITECTURE.md` §6.9)
**Definition of done:**
- [ ] `GET /api/routes/{route_id}/analysis` returns the full canonical profile
- [ ] Partial-failure guards: one domain down → profile still returned, other domains intact
- [ ] No opaque merged score introduced
**Lands in:** `backend/app/services/profile/`, `07_API_CONTRACT.md`.

### Phase 9 — LLM
**Prompt phase:** 10 (LLM).
**Goal:** Grounded natural-language explanation over verified structured data only.
**Key deliverables:**
- Structured-prompt builder from RouteProfile (`03_ARCHITECTURE.md` §6.11)
- LLM service + provider abstraction + output validation (`02_TRD.md` §95)
- Deterministic fallback when `LLM_API_KEY`/`LLM_BASE_URL` absent (`03_ARCHITECTURE.md` §6.11)
- LLM traceability (explanation → route profile → analysis id) per `02_TRD.md` §134
**Definition of done:**
- [ ] Grounding tests: explanation references only supplied structured data
- [ ] No invented hazards/facilities/distances/risk; no safety guarantees
- [ ] Provider failure → fallback text; structured analysis intact (`09_ERROR_HANDLING.md` §10.8)
- [ ] Prompt-injection / output-sanitization handled (`02_TRD.md` §47)
**Lands in:** `backend/app/services/llm/`, `12_LLM_SPEC.md`.

### Phase 10 — Production Hardening
**Prompt phases:** 11 (Production Security) + 12 (Testing) + 13 (Deployment).
**Goal:** Operable, secure, monitored, versioned, deployable production system.
**Key deliverables:**
- Caching keyed by model_version + config (`02_TRD.md` §85–§86)
- Structured logging + correlation + metrics per `16_MONITORING.md`
- Rate limiting, error handling completeness, security checks (`10_SECURITY.md`)
- Full test pyramid incl. failure/security tests (`13_TESTING.md`, `09_ERROR_HANDLING.md` §15)
- Deployment + rollback + backups + health checks per `15_DEPLOYMENT.md`
- Version matrix: app / API / schema / model / risk / config (`02_TRD.md` §164)
**Definition of done:**
- [ ] Every item in `03_ARCHITECTURE.md` §13 (Definition of Done) passes
- [ ] `14_PRODUCTION_CHECKLIST.md` passes before and after release
- [ ] Monitoring/alerting thresholds configured (baselined in staging)
- [ ] Backups + restore rehearsed; rollback rehearsed
- [ ] Secrets hygiene: no key in repo/logs/CI output
**Lands in:** caching/observability layers in `backend/`, `10_SECURITY.md`, `15_DEPLOYMENT.md`, `16_MONITORING.md`, CI workflows.

---

## 4. CURRENT STATUS

All items below are unchecked as of this document's creation. No build phase has been started (repository contains documentation only).

- [ ] Phase 1 — Foundation
- [ ] Phase 2 — Routing
- [ ] Phase 3 — Road Image Pipeline
- [ ] Phase 4 — YOLO11
- [ ] Phase 5 — Hazard Aggregation
- [ ] Phase 6 — Risk Engine
- [ ] Phase 7 — Facility Intelligence
- [ ] Phase 8 — Route Profile
- [ ] Phase 9 — LLM
- [ ] Phase 10 — Production Hardening

---

## 5. NEAR-TERM SPRINT MILESTONES

The first build horizon, in order, each ending in a shippable, verifiable state:

1. **Sprint A — Scaffold backend + health.** FastAPI app + config + DB engine + `GET /api/health` + Docker Compose + CI (lint/type/tests). *Gate:* health 200, Compose up, CI green.
2. **Sprint B — Routing OSRM.** `RoutingService` + OSRM provider + normalization + `POST /api/routes`; frontend draws polylines. *Gate:* up to 4 normalized routes, no fabricated routes, normalization tests.
3. **Sprint C — Image pipeline.** Segmentation + image retrieval + validation + OpenCV preprocessing. *Gate:* images fetched/validated/preprocessed per segment with metadata.
4. **Sprint D — YOLO11.** Dataset scaffold + training script + inference service + versioned detections. *Gate:* structured detections with model_version tags; dataset documented.
5. **Sprint E — Hazard aggregation + Risk engine.** Dedup/clustering + deterministic 0–100 score with documented formula and versioning. *Gate:* aggregation/risk unit tests; never zero-on-failure.
6. **Sprint F — Facilities.** Corridor search + Overpass + counts/nearest per category; zero ≠ unavailable. *Gate:* facilities associated to routes; provider-failure handled.
7. **Sprint G — Route profile + LLM fallback.** Canonical profile with partial guards + grounded LLM + deterministic fallback. *Gate:* `/analysis` returns full profile; grounding tests pass.
8. **Sprint H — Frontend basics.** Search form → route cards → map → detail page → hazard/facility markers → AI explanation, with loading/error/empty/partial states.
9. **Sprint I — Production hardening.** Caching, structured logging/metrics/alerting, rate limiting, security, full failure/security tests, deployment + rollback + backups, `14_PRODUCTION_CHECKLIST.md` gate.

Each sprint ends with the relevant Definition of Done of §3 checked and the affected tests green; no sprint start depends on a later phase.

---

## 6. RELATED DOCUMENTS

- `03_ARCHITECTURE.md` §11 (build order, DoD), §12 (verification commands), §13 (Definition of Done)
- `MASTER_PROJECT_PROMPT.md` §101 (13-phase plan), §42 (phase order), §118 (production checklist)
- `MASTER_RULES.md` §42 (development phases)
- `13_TESTING.md` (test plan per phase), `14_PRODUCTION_CHECKLIST.md` (release gate)
- `15_DEPLOYMENT.md`, `16_MONITORING.md`, `10_SECURITY.md`
- `16_CHANGELOG.md` (progress log), `17_DECISIONS.md` (architectural decisions)

---

# END OF DEVELOPMENT ROADMAP