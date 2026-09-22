# Architecture — SafeRoute AI

> **BUILD DIRECTIVE (read first)**
> This document is the single source of truth for building SafeRoute AI. If the user says **"build that"**, **"you build this project"**, or anything that refers to this project, follow this document **verbatim and without asking for clarification**. Implement every phase in order, ship real working code, and do not skip steps. Defaults are already decided below — do not ask which stack to use.

---

## 1. What This Project Is

SafeRoute AI is an intelligent route-analysis platform. The user enters **Source** and **Destination**. The system:

1. Generates **up to 4 candidate routes** from a routing provider
2. For each route, analyzes **road hazards** (potholes, cracks, damaged roads, obstacles, debris) via road images → OpenCV → YOLO11
3. Computes a **deterministic risk score**
4. Finds **nearby facilities** (hospitals, medical stores, pharmacies, restaurants, hotels, petrol pumps, police stations) within a configurable corridor
5. Produces a structured **Route Profile**, then an **LLM-generated explanation** grounded strictly in that structured data
6. Displays routes + full analysis in a **frontend** (map + route cards + detail page)

**Core principle:** *AI detects and explains; deterministic services calculate and retrieve; the user sees the evidence.*

The LLM never decides, never detects, never calculates, and never invents data.

---

## 2. Fixed Build Decisions (do not ask)

| Decision | Choice |
|----------|--------|
| Backend language | Python 3.11+ |
| Backend API framework | FastAPI |
| ORM / DB | SQLAlchemy 2.0 + PostgreSQL 16 |
| Routing provider (default) | OSRM public API (keyless, self-hostable later) |
| Facility provider (default) | Overpass API (OpenStreetMap, keyless) |
| Computer vision | opencv-python (preprocessing) |
| Detection model | YOLO11 via `ultralytics` |
| Model format | exported ONNX or PyTorch `.pt` from `ml/training`; path via `MODEL_PATH` |
| LLM | OpenAI-compatible chat-completions API (`LLM_BASE_URL` + `LLM_API_KEY`); degrades gracefully when key absent |
| Frontend | React + Vite + TypeScript, `react-leaflet` for the map |
| Async worker | Python `asyncio` (FastAPI BackgroundTasks); no Celery in v1 |
| Containerization | Docker Compose (backend, db, frontend optional) |
| Tests | pytest (backend), Vitest/React Testing Library (frontend) |
| Lint/checks | ruff + mypy (backend), eslint (frontend) |

All secrets via environment variables (`.env`, never committed). `.env.example` committed with placeholder values.

---

## 3. Repository Layout (build exactly this)

```
saferoute-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, wires routers + startup
│   │   ├── config.py                # pydantic-settings, all env vars
│   │   ├── api/
│   │   │   └── routers.py           # resource-oriented endpoints
│   │   ├── schemas/                 # Pydantic request/response models
│   │   ├── models/                  # SQLAlchemy entities
│   │   ├── db.py                    # engine, session, Base
│   │   └── services/
│   │       ├── routing/
│   │       │   ├── routing_service.py   # abstraction
│   │       │   ├── providers/osrm.py    # default provider
│   │       │   └── models/route.py      # normalized Route model
│   │       ├── vision/
│   │       │   ├── image_retrieval.py   # fetch road images per segment
│   │       │   ├── opencv_service.py    # preprocessing + quality checks
│   │       │   └── yolo_service.py      # YOLO11 inference, structured detections
│   │       ├── safety/
│   │       │   ├── hazard_aggregation.py  # image→segment→route aggregation
│   │       │   └── risk_engine.py         # deterministic score
│   │       ├── facilities/
│   │       │   ├── facility_service.py    # corridor search, counts, nearest
│   │       │   └── providers/overpass.py  # default facility provider
│   │       ├── profile/
│   │       │   └── route_profile.py       # canonical RouteProfile object
│   │       └── llm/
│   │           └── llm_service.py         # grounded explanation only
│   ├── tests/                      # pytest
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # search, route cards
│   │   ├── api/client.ts           # typed API client
│   │   ├── components/
│   │   │   ├── SearchForm.tsx
│   │   │   ├── RouteMap.tsx        # react-leaflet, route polylines
│   │   │   ├── RouteCard.tsx
│   │   │   ├── RouteDetail.tsx
│   │   │   ├── MarkerFilter.tsx    # toggle by category
│   │   │   └── icon.ts             # per-category marker config
│   │   └── types.ts                # TS types mirroring backend schemas
│   ├── package.json
│   └── vite.config.ts
├── ml/
│   ├── dataset/
│   │   ├── images/{train,val,test}/
│   │   ├── labels/{train,val,test}/
│   │   └── data.yaml
│   ├── training/train.py           # YOLO11 training script
│   └── models/                     # best.pt / best.onnx (gitignored)
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 4. System Overview

```
USER → FRONTEND → BACKEND API → ROUTE GENERATION → UP TO 4 CANDIDATE ROUTES
→ ROUTE NORMALIZATION
   ├─ ROAD SAFETY PIPELINE:  Road Images → OpenCV → YOLO11 → Hazard Detection
   └─ FACILITY PIPELINE:     Route Geometry → Corridor → Geographic Search → Facility Aggregation
→ ROUTE ANALYSIS ENGINE → RISK / ROUTE METRICS
   ├─ DATABASE
   └─ LLM → Explanation
→ FRONTEND (map + route cards + detail + explanation)
```

The **LLM sits at the end**. It receives only the verified structured Route Profile.

---

## 5. Multi-Route Design (mandatory)

- Represent routes as a dynamic collection: `routes: [route_1, route_2, route_3, route_4]`.
- Handle **1 to 4 routes** based on whatever the routing provider returns.
- **Never fabricate a route** to reach four.
- Process each route independently (async/parallel where supported). Route 2 never waits on Route 1.
- No hard-coded "Route A / Route B" anywhere.

---

## 6. Module Specifications

### 6.1 Route Generation + Normalization

`routing_service.py` exposes a `RoutingService` abstraction:

```
RoutingService
  ├── Provider implementation (OSRM)
  └── Normalized Route model
```

Normalized route model fields:
```json
{
  "route_id": "route_1",
  "distance_km": 8.2,
  "duration_minutes": 19,
  "geometry": [],
  "segments": []
}
```

Rules:
- Provider-specific responses are normalized **once** at this boundary; raw provider payloads never propagate.
- Provider failure → no routes → clear error, never a fake route.

### 6.2 Road Image Pipeline

Per route: `Route Geometry → Segments → Road Image Collection → Validation → Quality Check → OpenCV → YOLO11`.

Every image keeps metadata:
```
route_id, segment_id, image_id, latitude, longitude, timestamp?, source
```
so a hazard is always attributable to a route + location.

### 6.3 OpenCV Module

Responsibilities: loading, validation, resize, normalization, color conversion, noise reduction, contrast enhancement, quality checks, transformations.
- OpenCV is **preprocessing only**. It does not detect hazards. YOLO11 detects.
- Pipeline: `Raw Road Image → OpenCV preprocessing → YOLO11 inference`.

### 6.4 YOLO11 Module

- Model path from `MODEL_PATH` (env/config), **never hard-coded**.
- Returns structured detections:
```json
{
  "image_id": "image_001",
  "model": "SafeRoute-YOLO11",
  "model_version": "1.0.0",
  "detections": [
    { "class": "pothole", "confidence": 0.91,
      "bounding_box": { "x1": 100, "y1": 120, "x2": 300, "y2": 260 } }
  ]
}
```
- Each detection retains class, confidence, bbox, image_id, route_id, segment_id, geo info when available, and model version.
- Class list is defined by `ml/dataset/data.yaml` (defaults: `pothole`, `road_crack`, `damaged_road`, `obstacle`, `debris` — only what's in the dataset).

### 6.5 Training vs Inference

Two separate concerns:
```
Training Pipeline  (ml/training, dataset split train/val/test)
        ↓ best model (.pt/.onnx)
Production Inference Service  (MODEL_PATH)
```
The inference service never trains; the training script never runs in prod.

### 6.6 Hazard Aggregation

Image detections → route-level counts with duplicate suppression:
```
Image1: 2 potholes, Image2: 1 pothole, Image3: 2 cracks, Image4: 1 obstacle
        ↓  route-level
Potholes=3  Cracks=2  Obstacles=1
```
Use segment IDs, coordinates, spatial clustering, and overlap handling to avoid double counting.

### 6.7 Risk Engine (deterministic)

Formula (configurable weights, documented in code + `04` configs):
```
risk = Σ( hazard_weight(hazard) × confidence × severity(hazard) × exposure(segment) )
normalized → 0..100
```
- Never computed by the LLM.
- Not presented as an official road-safety standard.
- Route risk data payload:
```json
{
  "route_id": "route_1",
  "risk_score": 28,
  "hazard_summary": { "potholes": 3, "road_cracks": 2, "damaged_roads": 1, "obstacles": 1, "debris": 0 },
  "images_analyzed": 15,
  "segments_analyzed": 24,
  "model_version": "1.0.0"
}
```

### 6.8 Facility Intelligence Module

- Configurable category system (not hard-coded logic): hospitals, medical_stores (pharmacies), restaurants, hotels, petrol_pumps, police_stations.
- Extensible: future categories = ev_charging, fire_stations, atms, parking, vehicle_repair, tire_shops, emergency_services.
- **Corridor search**: only facilities within `FACILITY_SEARCH_RADIUS_KM` of the route are returned.
- Facility structured fields: `facility_id, name, category, latitude, longitude, distance_from_route_km, address?, phone?, opening_status?, source`.

Aggregation per route:
```json
{
  "hospitals": { "count": 3, "nearest_distance_km": 0.8 },
  "medical_stores": { "count": 7, "nearest_distance_km": 0.2 },
  "restaurants": { "count": 15, "nearest_distance_km": 0.1 },
  "hotels": { "count": 5, "nearest_distance_km": 0.6 },
  "petrol_pumps": { "count": 2, "nearest_distance_km": 0.9 },
  "police_stations": { "count": 1, "nearest_distance_km": 1.2 }
}
```

### 6.9 Safety vs Convenience — NEVER merged

```
ROUTE PROFILE
├── Road Safety            → hazard score, count, density
├── Emergency Accessibility → hospitals, medical stores, police stations
├── Travel Convenience     → restaurants, hotels, petrol pumps
└── Route Information      → distance, duration
```
More restaurants/hotels ≠ safer road.

### 6.10 Route Profile Engine

Canonical structured object consumed by the frontend and LLM:
```json
{
  "route_id": "route_1",
  "route": { "distance_km": 8.2, "duration_minutes": 19 },
  "safety": { "risk_score": 28, "hazards": { "potholes": 3, "cracks": 2, "obstacles": 1 } },
  "facilities": { "hospitals": 3, "medical_stores": 7, "restaurants": 15,
                  "hotels": 5, "petrol_pumps": 2, "police_stations": 1 }
}
```

### 6.11 LLM Layer (grounded explanation)

- Input: **only** the structured Route Profile (no free-form). Example:
```json
{
  "route_id": "route_1", "distance_km": 8.2, "duration_minutes": 19,
  "risk_score": 28, "hazards": { "potholes": 3, "cracks": 2 },
  "facilities": { "hospitals": 3, "medical_stores": 7, "petrol_pumps": 2, "police_stations": 1 }
}
```
- Output: a natural-language explanation restricted to those facts.
- **Grounding rules (hard):**
  1. Never invent a facility, hazard, or route
  2. Never modify the numerical risk score
  3. No real-time claims unless backend provides it
  4. Distinguish detected vs estimated info
  5. Use only backend-provided structured data; say "unavailable" if absent
  6. No "completely safe" claims; no guarantee-of-safety language
- If `LLM_API_KEY`/`LLM_BASE_URL` missing → return a deterministic fallback sentence built from the structured data (never an error that kills the route).

---

## 7. Backend API Contract

Resource-oriented endpoints. Endpoint bodies must be strictly typed Pydantic schemas.

```
POST /api/routes                  # body: {source, destination} → {routes: [route summary ×N]}
GET  /api/routes/{route_id}       # normalized route detail
POST /api/routes/{route_id}/analyze   # run full pipeline for one route
GET  /api/routes/{route_id}/hazards
GET  /api/routes/{route_id}/facilities
GET  /api/routes/{route_id}/analysis    # full RouteProfile incl. explanation
POST /api/llm/explanation          # LLM over a supplied structured profile
GET  /api/health                  # liveness
```

Error envelope (all endpoints):
```json
{ "error": { "code": "ROUTE_NOT_FOUND", "message": "..." } }
```
Error catalog (at minimum): `INVALID_SOURCE`, `INVALID_DESTINATION`, `NO_ROUTE_FOUND`, `ROUTING_PROVIDER_FAILURE`, `ROUTE_NOT_FOUND`, `IMAGE_UNAVAILABLE`, `YOLO_FAILURE`, `FACILITY_PROVIDER_FAILURE`, `LLM_FAILURE`, `RATE_LIMITED`.

Partial failure rule: `YOLO unavailable → route + facilities still returned; safety marked unavailable`. Never fabricate missing results.

---

## 8. Configuration (`.env.example`)

```env
DATABASE_URL=postgresql+psycopg://saferoute:saferoute@db:5432/saferoute
ROUTING_PROVIDER=osrm
ROUTING_BASE_URL=https://router.project-osrm.org
FACILITY_PROVIDER=overpass
OVERpass_BASE_URL=https://overpass-api.de/api/interpreter   # note: OVERPASS_*
FACILITY_SEARCH_RADIUS_KM=1.0
MODEL_PATH=ml/models/best.pt
MODEL_NAME=SafeRoute-YOLO11
MODEL_VERSION=1.0.0
HAZARD_WEIGHTS=pothole:3,road_crack:2,damaged_road:2,obstacle:1,debris:1
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=
LLM_MODEL=gpt-4o-mini
MAX_ROUTES=4
CACHE_ENABLED=true
```
(All values overridable via env; `OVERPass_*` typo is intentional to be fixed as `OVERPASS_BASE_URL`).

---

## 9. Data Model (SQLAlchemy entities)

`users` (optional, v1 can skip) · `route_requests` · `routes` · `route_segments` · `road_images` · `hazards` · `facilities` · `route_facilities` · `route_analysis` · `model_versions`.

Relationships:
```
route_request 1─N routes
route 1─N route_segments
route_segment 1─N road_images
road_image 1─N hazards
route N─N facilities (route_facilities)
route 1─1 route_analysis
hazards / road_images FK → model_versions
```
Every hazard row stores: class, confidence, bbox, image_id, segment_id, route_id, latitude/longitude, model_version. This satisfies data provenance + model versioning.

---

## 10. Frontend Requirements

- **Search**: Source, Destination, `[Analyze Routes]`.
- **Map**: route polylines for each returned route; toggle layers for hazards + each facility category.
- **Route Cards** (per route): Route, Distance, Duration, Risk Score, Detected Hazards, Nearby counts per category.
- **Route Detail** (on select): overview → map → road hazard analysis → detected hazard locations → risk metrics → nearby facilities → LLM explanation (grouped per `6.9`).
- **Markers**: distinct per category (hazards, hospitals, medical_stores, restaurants, hotels, petrol_pumps, police_stations); filterable.
- Typed client mirrors backend schemas. Loading / error / empty / offline states everywhere.

---

## 11. Build Order (implement each phase to its Definition of Done, in order)

> Do not skip to "nice-to-haves." Complete each phase before the next.

### Phase 1 — Foundation
Backend scaffold (FastAPI + config + db + health), frontend scaffold (Vite + React + map), docker-compose, `.env.example`, CI (lint, tests).
**DoD:** `GET /api/health` returns 200; frontend renders; Docker Compose up works.

### Phase 2 — Routing
`RoutingService` + OSRM provider + route normalization + `POST /api/routes`. Frontend draws returned route polylines.
**DoD:** source+destination returns up to 4 normalized routes; unit tests for normalization.

### Phase 3 — Road Image Pipeline
Segments, image retrieval service, validation, OpenCV preprocessing.
**DoD:** images fetch/validate/preprocess per segment with metadata attached.

### Phase 4 — YOLO11
`ml/training/train.py` + dataset scaffold + `yolo_service.py` inference + structured detections.
**DoD:** running inference returns structured detections with image/route/segment/model_version tags.

### Phase 5 — Hazard Aggregation
image → segment → route hazard counts with dedup/spatial clustering.
**DoD:** aggregation unit tests; no double counting on overlapping images.

### Phase 6 — Risk Engine
Configurable weights; deterministic score; `risk_score` in payload.
**DoD:** known-input → expected-score unit tests.

### Phase 7 — Facility Intelligence
Corridor search via Overpass, counts + nearest per category, configurable radius.
**DoD:** facilities associated to the correct route; tests.

### Phase 8 — Route Profile
Combine route + hazards + risk + facilities + (partial-failure guards).
**DoD:** `/api/routes/{id}/analysis` returns full canonical profile.

### Phase 9 — LLM
Grounded explanation + deterministic fallback when key absent.
**DoD:** grounding tests — explanation only references supplied structured data.

### Phase 10 — Production Hardening
Caching (keyed by model_version+config), logging (`request_id`, `route_id`, stage, duration, model_version, error_type; never secrets), rate limiting, error handling, full tests, security checks, model versioning, performance (batching, connection pooling, image resize).

**Final DoD:** every item in the checklist §13 passes.

---

## 12. Verification Commands (run at the end)

Backend:
```bash
cd backend
ruff check .
mypy app
pytest -q
uvicorn app.main:app --reload   # manual smoke: /api/health, POST /api/routes
```
Frontend:
```bash
cd frontend
npm run lint
npm test
npm run build
npm run dev
```
Integration smoke:
```bash
curl -X POST http://localhost:8000/api/routes -d '{"source":"A","destination":"B"}'
curl http://localhost:8000/api/routes/route_1/analysis
```

**If the user says "build that" / "you build this":** run the build order §11 top to bottom, using the fixed decisions in §2, then report in this format:

```
## Changes
- file/module → change

## Verification
- tests/lint/build → result

## Notes
- only important remaining limitations
```

---

## 13. Definition of Done (every item must pass)

```
✓ Requirement implemented
✓ Existing functionality preserved
✓ Backend works (all declared endpoints return correct typed payloads)
✓ Frontend works (search, map, cards, detail, filters)
✓ API contracts validated
✓ Error handling implemented (catalog §7)
✓ Important logic tested (routing, normalization, aggregation, risk, facilities, LLM grounding, API)
✓ YOLO integration verified
✓ Risk calculation verified (deterministic, documented)
✓ Facility analysis verified (counts + nearest per category)
✓ LLM receives structured data only
✓ No fabricated data anywhere
✓ Configuration externalized (no hard-coded model paths/keys)
✓ Secrets protected (.env only)
✓ ruff / mypy / pytest / eslint / build pass
```

---

## 14. Non-Negotiable Rules

- Inspect the repo before modifying; reuse existing architecture.
- Support multiple routes dynamically; never hard-code two routes.
- Keep YOLO detection, risk calculation, facility analysis, and LLM generation as separate modules.
- Never fabricate missing data; never hard-code secrets; never silently ignore errors.
- Add tests for important logic; verify before reporting done.
- Avoid unnecessary dependencies and rewrites; preserve existing functionality.

---

## 15. Related Docs

- `00_MASTER_RULES.md` — governing rules
- `04_DATA_MODEL.md` — entity-level schema
- `07_API_CONTRACT.md` — endpoint-level contract
- `13_TESTING.md` — test plan
- `14_PRODUCTION_CHECKLIST.md` — release gate
- `runbooks/database-migration-failure.md`, `runbooks/credential-reevocation-or-leak.md` — incident procedures