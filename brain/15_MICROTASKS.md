# 15_MICROTASKS.md — SafeRoute AI Microtasks

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Shippable Microtask Breakdown
**Version:** 1.0
**Status:** Implementation-Ready
**Authority:** `03_ARCHITECTURE.md` §11 (build order) > `02_TRD.md` > this document
**Companion:** `13_TESTING.md` (test requirements), `16_CHANGELOG.md` (release notes)

Small, shippable units of work grouped by project phase (`MASTER_PROJECT_PROMPT.md` §101, `03_ARCHITECTURE.md` §11). Check off as completed. One feature per change; each change includes tests; record completion in `16_CHANGELOG.md`.

---

## Phase 1 — Foundation (backend scaffold + health, config, db, docker-compose, .env.example, CI)

- [ ] Scaffold `backend/` FastAPI project structure (`app/main.py`, `config.py`, `api/`, `schemas/`, `models/`, `db.py`, `services/`) per `03_ARCHITECTURE.md` §3
- [ ] Scaffold `frontend/` React + Vite + TypeScript project with `react-leaflet` map
- [ ] Scaffold `ml/` layout: `dataset/`, `training/`, `models/` (`03_ARCHITECTURE.md` §3)
- [ ] Implement `app/config.py` with `pydantic-settings` and all env vars (`DATABASE_URL`, providers, model, LLM, risk, limits) (`03_ARCHITECTURE.md` §8)
- [ ] Implement database engine/session/Base (SQLAlchemy 2.0 + PostgreSQL 16)
- [ ] Wire Alembic migrations baseline (no tables yet or minimal schema)
- [ ] Add health endpoints `GET /api/v1/health` (liveness) and readiness reporting component availability (`07_API_CONTRACT.md` §7.17)
- [ ] Create `docker-compose.yml` (backend, db; frontend optional) (`03_ARCHITECTURE.md` §2)
- [ ] Create `.env.example` with placeholder values; ensure `.env` gitignored
- [ ] Add CI workflow: ruff, mypy, pytest, eslint, vitest, build, security scans (`02_TRD.md` §126, `12_GITHUB_ACTIONS.md`)
- [ ] Add backend test scaffolding: `pytest`, `tests/unit/`, `tests/api/`, fixtures layout (`02_TRD.md` §114)
- [ ] Add frontend test scaffolding: Vitest + React Testing Library
- [ ] Verify smoke: `GET /api/v1/health` returns healthy; frontend renders; docker compose up works (`03_ARCHITECTURE.md` §11 Phase 1 DoD)

## Phase 2 — Routing (OSRM provider, normalization, POST /api/v1/route-requests)

- [ ] Implement `RoutingService` abstraction (`route()`, normalize boundary) (`02_TRD.md` §94)
- [ ] Implement OSRM provider adapter (keyless public API; base URL configurable) (`05_DATA_SOURCES.md` §1)
- [ ] Implement route normalization from OSRM response → internal `Route` model (`route_id`, `distance_meters`, `duration_seconds`, `geometry`, `coordinates`, `segments`, `provider`, `provider_route_id`) (`02_TRD.md` §12)
- [ ] Implement route geometry canonicalization (single internal format) (`02_TRD.md` §14, `07_API_CONTRACT.md` §7.5)
- [ ] Implement route segmentation into `RouteSegment`s with sequence order (`02_TRD.md` §13)
- [ ] Implement request/response schemas for `POST /api/v1/route-requests` (`07_API_CONTRACT.md` §7.1)
- [ ] Implement coordinate validation (lat/lon ranges, types, missing) (`02_TRD.md` §57)
- [ ] Implement error mapping: `INVALID_SOURCE`, `INVALID_DESTINATION`, `NO_ROUTE_FOUND`, `ROUTING_PROVIDER_ERROR` (`07_API_CONTRACT.md` §9)
- [ ] Support dynamic 1–4 routes; never pad; no hard-coded Route A/B (`MASTER_RULES.md` §6)
- [ ] Unit tests: normalization (1–4 routes), coordinate validation, error mapping (`13_TESTING.md` §5)
- [ ] API tests: valid/invalid/missing fields/bad coords/no route/provider failure (`13_TESTING.md` §8)
- [ ] Mock OSRM provider for all automated tests; no live network dependency (`02_TRD.md` §115)
- [ ] Frontend: typed client for route-request; draw returned route polylines on map (`03_ARCHITECTURE.md` §11 Phase 2 DoD)

## Phase 3 — Road Image Pipeline

- [ ] Implement `image_retrieval.py` to fetch/collect road images per segment with metadata (`route_id`, `segment_id`, `image_id`, `source`, `lat/lon`, `timestamp`, `file_reference`) (`02_TRD.md` §16)
- [ ] Implement image validation (existence, MIME, extension, size, readability, dimensions, corruption) (`02_TRD.md` §17)
- [ ] Implement image quality checks (resolution, blur, exposure, occlusion) with recorded reasons (`02_TRD.md` §18)
- [ ] Implement OpenCV preprocessing service (load, validate, resize, color convert, noise reduction, contrast, normalize) (`02_TRD.md` §19)
- [ ] Enforce OpenCV = preprocessing only; never presented as the detector (`02_TRD.md` §20)
- [ ] Persist `road_images` rows with `processing_status`; invalid images marked `invalid` (`04_DATA_MODEL.md` §7.6)
- [ ] Unit tests: image validation, OpenCV preprocessing, quality gates, invalid/corrupt/oversized inputs (`13_TESTING.md` §9)
- [ ] Failure tests: image unavailable → segment "not analyzed", never "no hazards" (`09_ERROR_HANDLING.md` §10.2)
- [ ] Frontend: show image/segment evidence where available (Phase 3 DoD per `03_ARCHITECTURE.md` §11)

## Phase 4 — YOLO11 Inference Service + Dataset Scaffold

- [ ] Scaffold `ml/dataset/` structure: `images/{train,val,test}`, `labels/{train,val,test}`, `data.yaml` (`MASTER_RULES.md` §9)
- [ ] Create `ml/training/train.py` (YOLO11 training entrypoint; never runs in prod) (`03_ARCHITECTURE.md` §6.5)
- [ ] Implement `yolo_service.py` model loading once per process from `MODEL_PATH` (`02_TRD.md` §91)
- [ ] Implement YOLO11 inference returning structured `HazardDetection` (class, confidence, bbox, image/route/segment ids, lat/lon, model_version) (`02_TRD.md` §22, §26)
- [ ] Implement class mapping from `data.yaml` (dataset classes → model classes → app classes) (`02_TRD.md` §23)
- [ ] Implement confidence filtering against configured `YOLO_CONFIDENCE_THRESHOLD` (`02_TRD.md` §24)
- [ ] Record model provenance: name/version/dataset version; model versioning tracked (`02_TRD.md` §25, `04_DATA_MODEL.md` §7.13)
- [ ] Model load failure → `YOLO status = unavailable`; service stays up (`09_ERROR_HANDLING.md` §10.4)
- [ ] Support CPU inference; optional GPU device selection configurable; never assume GPU (`02_TRD.md` §90)
- [ ] ML tests: model loading, preprocessing, detection parsing, class mapping, confidence filtering, empty detections, invalid images, model failure (`13_TESTING.md` §9)
- [ ] Persist `hazards` rows traceable to `model_version` (Phase 4 DoD per `03_ARCHITECTURE.md` §11)

## Phase 5 — Hazard Aggregation

- [ ] Implement image-level → segment-level → route-level hazard aggregation (`02_TRD.md` §28)
- [ ] Implement duplicate suppression (geographic proximity, segment association, overlap, spatial clustering) (`02_TRD.md` §27)
- [ ] Ensure the same hazard in overlapping images is not double-counted (`MASTER_RULES.md` §12)
- [ ] Produce hazard summary per route: `potholes`, `road_cracks`, `damaged_roads`, `obstacles`, `debris` (`02_TRD.md` §29)
- [ ] `GET /api/v1/routes/{route_id}/hazards` endpoint (`07_API_CONTRACT.md` §7.10)
- [ ] Unit tests: none/one/multiple, duplicates, overlapping, clusters (`13_TESTING.md` §5.3)
- [ ] Failure test: aggregation config error → fail fast; partial clustering → `status=partial` (`09_ERROR_HANDLING.md` §10.5)
- [ ] Endpoints expose aggregated hazards with traceability to segments/route/images (Phase 5 DoD per `03_ARCHITECTURE.md` §11)

## Phase 6 — Risk Engine

- [ ] Implement deterministic risk calculator: Σ(weight × severity × confidence × exposure) (`MASTER_RULES.md` §13, `03_ARCHITECTURE.md` §6.7)
- [ ] Implement weight configuration parse (`HAZARD_WEIGHTS`) from config, never hard-coded (`MASTER_RULES.md` §24)
- [ ] Document the formula and normalization in risk-engine docs (`02_TRD.md` §32, §155)
- [ ] Implement risk score normalization to 0–100 consistently (`02_TRD.md` §34)
- [ ] Handle missing data → `risk_status=unavailable`, never `score=0` (`09_ERROR_HANDLING.md` §10.6)
- [ ] Risk engine versioning; results traceable to config version (`MASTER_PROJECT_PROMPT.md` §112)
- [ ] `GET /api/v1/routes/{route_id}/risk` endpoint (`07_API_CONTRACT.md` §7.12)
- [ ] Risk tests: no/single/multiple hazards, low/high confidence, class variety, max values, missing data, determinism (`13_TESTING.md` §6)
- [ ] Persist `route_analysis` rows with `risk_score`, counts, model version (Phase 6 DoD per `03_ARCHITECTURE.md` §11)

## Phase 7 — Facilities / Overpass

- [ ] Implement `FacilityService` abstraction (`search()`, normalize, health check) (`02_TRD.md` §93)
- [ ] Implement Overpass (OSM) provider adapter, keyless, base URL configurable (`05_DATA_SOURCES.md` §3)
- [ ] Implement route-corridor search buffer (`FACILITY_SEARCH_RADIUS_KM`), never whole-city search (`MASTER_PROJECT_PROMPT.md` §23)
- [ ] Implement facility normalization: `facility_id`, `name`, `category`, `lat/lon`, `distance_from_route_km`, `address?`, `phone?`, `opening_status?`, `source` (`MASTER_RULES.md` §15)
- [ ] Implement categories: hospital, medical_store, restaurant, hotel, petrol_pump, police_station, separated into emergency accessibility vs travel convenience (`MASTER_RULES.md` §14)
- [ ] Implement facility deduplication (provider ID preferred; then coordinates/name/address) (`02_TRD.md` §39)
- [ ] Implement distance-from-route calculation (straight-line, never described as driving) (`02_TRD.md` §40)
- [ ] Aggregate counts + nearest distance per category (`02_TRD.md` §41)
- [ ] `GET /api/v1/routes/{route_id}/facilities` and `/facilities/summary` endpoints (`07_API_CONTRACT.md` §7.13–§7.14)
- [ ] Facility tests: none/one/many, duplicates, categories, provider failure, missing coordinates (`13_TESTING.md` §7)
- [ ] Failure handling: provider error → `unavailable`, never zero; route/safety preserved (`09_ERROR_HANDLING.md` §10.7)
- [ ] Persist `facilities` + `route_facilities` rows with provider IDs (Phase 7 DoD per `03_ARCHITECTURE.md` §11)

## Phase 8 — Route Profile + Analysis Endpoint

- [ ] Implement `RouteProfile` service combining route + hazards + risk + facilities + processing status (`02_TRD.md` §43)
- [ ] Keep Road Safety, Emergency Accessibility, Travel Convenience, Route Information as separate dimensions; never merge into one arbitrary score (`MASTER_RULES.md` §14)
- [ ] Encode zero vs unavailable per domain in the profile (`02_TRD.md` §141)
- [ ] Implement partial-failure guards so one failed subsystem never destroys the full profile (`09_ERROR_HANDLING.md` §10)
- [ ] `POST /api/v1/routes/{route_id}/analysis` starts analysis; `GET /api/v1/routes/{route_id}/analysis` returns profile (`07_API_CONTRACT.md` §7.6, §7.15)
- [ ] Async analysis via FastAPI BackgroundTasks; job status via `GET /api/v1/jobs/{job_id}` with states queued/processing/partial/completed/failed (`02_TRD.md` §82–§84, `07_API_CONTRACT.md` §7.7)
- [ ] Idempotency guard for analysis POSTs (`Idempotency-Key`, `07_API_CONTRACT.md` §11.7)
- [ ] Persist `route_analysis` + `analysis_jobs` rows
- [ ] Route-profile unit tests (combination, partial envelopes) (`13_TESTING.md` §10.3)
- [ ] `GET /api/v1/routes/{route_id}/analysis` returns the canonical profile (Phase 8 DoD per `03_ARCHITECTURE.md` §11)

## Phase 9 — LLM Grounded + Fallback

- [ ] Implement `LLMService` abstraction (`generate_explanation()`, `validate_output()`, `handle_error()`) (`02_TRD.md` §95)
- [ ] Implement OpenAI-compatible chat-completions client configured via `LLM_BASE_URL` + `LLM_API_KEY` (`03_ARCHITECTURE.md` §2)
- [ ] Build grounded prompt from the structured Route Profile only (never free-form client data) (`MASTER_PROJECT_PROMPT.md` §34)
- [ ] Enforce grounding rules in the system instruction: no invented hazards/facilities/distances/scores; no guarantees of safety (`MASTER_PROJECT_PROMPT.md` §35–§36)
- [ ] Implement LLM output validation; unsupported numerical claims flagged (`02_TRD.md` §48)
- [ ] Implement deterministic fallback explanation when `LLM_API_KEY` absent or provider fails (`03_ARCHITECTURE.md` §6.11, `09_ERROR_HANDLING.md` §10.8)
- [ ] `POST /api/v1/llm/explanations` endpoint accepting a route-analysis identifier (not arbitrary numbers) (`07_API_CONTRACT.md` §7.16, `02_TRD.md` §56)
- [ ] LLM traceability: provider, model, prompt version, input version, timestamp (`02_TRD.md` §113)
- [ ] LLM tests: grounding (explanation only references supplied data), fallback on failure, output validation (`13_TESTING.md` §5.6, §10.1)
- [ ] Frontend: label explanation clearly as AI-generated; structured data remains authoritative (`MASTER_PROJECT_PROMPT.md` §77)
- [ ] Secure rendering of LLM text (no raw HTML); sanitize untrusted provider/LLM strings (Phase 9 DoD per `03_ARCHITECTURE.md` §11)

## Phase 10 — Production Hardening (caching, logging, rate limiting, tests, security)

- [ ] Implement caching keyed by route geometry hash + provider + model version + config; invalidation rules (`02_TRD.md` §85–§86)
- [ ] Implement structured logging: `request_id`, `route_id`, `job_id`, `stage`, `duration_ms`, `error_code`, `provider`, `model_version`; never log secrets (`MASTER_RULES.md` §32)
- [ ] Implement rate limiting on expensive endpoints (route generation, analysis, image upload, LLM) (`07_API_CONTRACT.md` §11.8, `MASTER_PROJECT_PROMPT.md` §107)
- [ ] Implement provider timeout + bounded retry policies (exponential backoff, idempotency-safe) (`02_TRD.md` §96–§98, `09_ERROR_HANDLING.md` §11)
- [ ] Implement request validation + request size limits everywhere (`02_TRD.md` §75)
- [ ] Security hardening: secure headers, CORS, upload validation, prompt-injection defenses, XSS-safe rendering (`security_handling.md`)
- [ ] Execute full security test pass: XSS, SQLi, upload abuse, prompt injection, malicious LLM output, rate-limit bypass, secret exposure (`13_TESTING.md` §12)
- [ ] Run full failure-test pass per `09_ERROR_HANDLING.md` §15 (isolation, zero vs unavailable, partial envelopes)
- [ ] Performance pass: batching, connection pooling, image resizing, DB index verification (`02_TRD.md` §87, §70)
- [ ] Model artifact checksummed + versioned for production (`02_TRD.md` §162)
- [ ] Add E2E test: source → dest → routes → analysis → hazards → facilities → explanation (`13_TESTING.md` §11)
- [ ] Frontend tests: loading/error/empty/partial/unavailable states + a11y/keyboard (`13_TESTING.md` §14)
- [ ] Production release checklist pass (`14_PRODUCTION_CHECKLIST.md`); changelog + decisions updated (`16_CHANGELOG.md`, `17_DECISIONS.md`)

---

## Process

- One feature per change (per PR where possible); no unrelated edits (`02_TRD.md` §147)
- Each change includes tests or verification where meaningful (`MASTER_RULES.md` §31)
- Meaningful commit messages per `02_TRD.md` §127 (`feat:`, `fix:`, `test:`, `docs:`)
- Branching: `main` / `develop` / `feature/*` / `fix/*` (`02_TRD.md` §128)
- Update this file as items complete (also record in `16_CHANGELOG.md`)
- Temporary/mock implementations clearly marked `DEMO`/`MOCK`; never silently in production (`02_TRD.md` §149–§150)
- Each phase reaches its Definition of Done (`03_ARCHITECTURE.md` §11, §13) before the next phase starts

---

# END OF MICROTASKS