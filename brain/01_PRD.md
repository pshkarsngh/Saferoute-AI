# Product Requirements Document (PRD) — SafeRoute AI

Version: 1.0
Project: SafeRoute AI — Intelligent Road Safety Navigation System
Project Type: Major College Project
Status: Production-Oriented Development

---

## 1. Vision

SafeRoute AI is an intelligent route-analysis platform that helps users choose safer travel routes.

A user enters a **source** and a **destination**. The system:

1. Generates **up to 4 candidate routes** from a routing provider.
2. Analyzes **road hazards** on each route (potholes, road cracks, damaged roads, obstacles, debris) using real road imagery processed by **OpenCV** and detected by a **YOLO11** model.
3. Aggregates detections into route/segment-level **hazard counts**.
4. Computes a **deterministic risk score** (0–100) from a documented, configurable risk engine.
5. Discovers **nearby facilities** (hospitals, medical stores, restaurants, hotels, petrol pumps, police stations) inside a configurable corridor around each route.
6. Combines all verified structured data into a **Route Profile**.
7. Uses an **LLM only to explain** the verified results in natural language.
8. Presents routes, hazards, risk, facilities, and the explanation to the user through a **frontend** map and route cards.

**Core principle:** *AI detects and explains; deterministic services calculate and retrieve; the user sees the evidence and route information needed to make their own choice.*

---

## 2. Problem Statement

Travelers routinely pick routes based only on distance, time, and traffic — not on **road condition or safety**.

Common problems:

- Roads with potholes, cracks, and debris cause vehicle damage, accidents, and delays.
- Commuters do not know which of several possible routes is in better road condition.
- There is no simple way to compare routes by detected hazard density.
- Emergencies require awareness of nearby hospitals, medical stores, and police stations — information that is not typically shown while choosing a route.
- Existing navigation apps show "fastest" routes but do not surface objective road-hazard analysis.

SafeRoute AI solves this by providing **evidence-based route comparison**: real detected hazards, a deterministic risk score, and nearby critical facilities for every candidate route.

---

## 3. Goals & Objectives

### Product Goals

- Provide safety-aware route comparison for up to 4 candidate routes.
- Make road-hazard information objective, image-based, and verifiable.
- Keep every number (distance, duration, risk, facility counts) deterministic and sourced — never AI-invented.

### Technical Objectives

- Modular, scalable architecture (routing, vision, detection, risk, facilities, profile, LLM, frontend).
- Support any number of routes from 1 to 4 dynamically.
- Configurable model paths, radiuses, weights, and thresholds — no hard-coded values.
- Model versioning and data provenance for reproducibility.
- Graceful partial failures (e.g., YOLO down → route + facilities still returned).

---

## 4. Target Audience

**Primary**

- Daily commuters choosing routes to work or study.
- Delivery riders and drivers who value predictable road conditions.
- College students and faculty (project demonstration, research, and extension).

**Secondary**

- Emergency planning use cases (knowing nearby hospitals/police).
- Local transport researchers interested in urban road-quality data.

Audience profile: users who already use map/navigation apps and want an extra **safety dimension** in route choice. No installation-heavy enterprise setup; this is a web-based dashboard/application.

---

## 5. Core Features

### F1 — Search (Source → Destination)

- Two inputs: **Source** and **Destination** (place name or coordinates).
- `[Analyze Routes]` button triggers route generation + full analysis.

### F2 — Up to 4 Candidate Routes

- Routing provider generates alternative routes.
- System dynamically handles 1, 2, 3, or 4 routes — never fabricates routes.
- Each route is unique (Route 1/2/3/4 or `route_1`…`route_4`).

### F3 — Route Information

Per route:

- Distance (km)
- Estimated duration (min)
- Route geometry + coordinates
- Route segments

### F4 — Road Hazard Detection

- Road imagery per route segment collected where available.
- OpenCV preprocessing (validation, resize, normalization, enhancement).
- YOLO11 detection of hazards: pothole, road_crack, damaged_road, obstacle, debris (classes limited to the annotated dataset).
- Every detection carries: class, confidence, bounding box, image/route/segment IDs, geo info, model version.

### F5 — Hazard Aggregation

- Image-level detections aggregated to segment and route level.
- Duplicate suppression: overlapping images / spatial clustering prevent double counting.

### F6 — Deterministic Risk Score

- Project-defined risk score, normalized **0–100**.
- Configurable weights: hazard type × severity × confidence × exposure.
- Clearly labeled as a project metric, **not** an official safety standard.

### F7 — Nearby Facilities

Per route (inside configurable corridor radius, e.g. `FACILITY_SEARCH_RADIUS_KM`):

- Hospitals
- Medical stores / pharmacies
- Restaurants
- Hotels
- Petrol pumps / fuel stations
- Police stations

For each category: **count** and **nearest distance from route**. Facility categories are configurable/extensible.

### F8 — Route Profile

Canonical combined object:

```
Route information
+ Road hazard information
+ Risk information
+ Nearby facility information
```

### F9 — LLM Explanation (Grounded)

- Receives only the structured Route Profile.
- Explains route differences, hazards, risk, and facilities in natural language.
- Strictly grounded: never invents data, never modifies the score, never claims "completely safe".

### F10 — Frontend Experience

- Map with route polylines (up to 4).
- Toggle markers: hazards + each facility category.
- Route cards: Route, Distance, Duration, Risk Score, Hazards, Facilities.
- Route detail page: overview → map → hazard analysis → risk metrics → facilities → LLM explanation.

---

## 6. Functional Requirements

| ID | Requirement | Acceptance |
|----|-------------|------------|
| FR-01 | Accept source/destination input | Invalid input returns typed error |
| FR-02 | Generate up to 4 candidate routes | Provider response normalized; fewer than 4 → analyze only those |
| FR-03 | Normalize each route | Common model: route_id, distance_km, duration_minutes, geometry, segments |
| FR-04 | Collect road images per segment | Images tagged with route_id, segment_id, image_id, coordinates |
| FR-05 | Validate + quality-check images | Bad images rejected, not counted as no-hazard |
| FR-06 | YOLO11 inference returns structured detections | class, confidence, bbox, image/route/segment, model_version |
| FR-07 | Aggregate detections to route level | Deduplication applied to overlapping images |
| FR-08 | Compute deterministic risk score (0–100) | Same inputs → same score; documented formula |
| FR-09 | Search facilities within corridor | Only facilities within radius returned; counts + nearest distance |
| FR-10 | Build canonical Route Profile | Contains route + safety + facilities (+ unavailable flags) |
| FR-11 | LLM explanation from profile only | Never invents data; safe fallback when key missing |
| FR-12 | Frontend displays all routes + analysis | Map, route cards, detail, marker filters, LLM explanation |

---

## 7. Non-Functional Requirements

| # | Category | Requirement |
|---|----------|-------------|
| NFR-01 | Performance | Route analysis completes with sensible latency; expensive steps (image retrieval, YOLO, LLM) async/batched where possible |
| NFR-02 | Reliability | Partial failure tolerated: YOLO down → route + facilities returned with safety marked unavailable |
| NFR-03 | Security | No secrets in code; env-var config; input validation; rate limiting; no sensitive data logged |
| NFR-04 | Maintainability | Modular services, typed schemas, documented risk formula, config-driven |
| NFR-05 | Accuracy & provenance | Every value traceable to source (routing provider, YOLO + image id, facility provider); model_version recorded |
| NFR-06 | Configurability | Model path, radius, weights, thresholds, route limit, provider URLs all configurable |
| NFR-07 | Testability | Core logic unit-tested: normalization, aggregation, risk, facilities, LLM grounding, API |
| NFR-08 | Scalability | Process 4 routes independently; architecture ready for queues/workers only when needed |

---

## 8. User Stories

- As a **commuter**, I want to compare several routes by road hazards so I can pick the safer road.
- As a **driver**, I want to know how many potholes/cracks each route has so I avoid vehicle damage.
- As a **user in an emergency**, I want to see nearby hospitals and police stations along a route.
- As a **researcher**, I want each risk value to come from real detected data so the analysis is trustworthy.
- As a **project evaluator**, I want a clear explanation of why Route 2 was scored safer than Route 1.

---

## 9. Out of Scope (v1)

- Routing directions/step-by-step turn-by-turn navigation voice.
- Live traffic-based re-routing (traffic is not a v1 data source).
- Real-time road imagery streaming; images come from available sources at analysis time.
- User accounts, login, saved route history, social features.
- Crowdsourced hazard reporting (future idea only).
- Mobile native apps (v1 is a web dashboard).
- Any unrelated feature per `00_MASTER_RULES.md` §4.

---

## 10. Success Metrics

- Analyzes requests: number of successful route analyses.
- Routes per request: average count (target up to 4).
- Analysis success rate: percentage of requests with full profile (route + safety + facilities + explanation).
- Detection coverage: % of analyzed segments with valid imagery.
- Risk determinism: unit tests asserting identical inputs → identical scores.
- LLM availability: % of explanations generated (with fallback reported).
- API latency: p95 of `/api/routes/{id}/analysis`.

---

## 11. Constraints & Assumptions

### Constraints

- Hazard classes limited to the project's annotated dataset (no invented classes).
- Risk score is project-defined; must not be presented as official/govt standard.
- LLM must never calculate scores or invent facts.
- Facility searches bounded by route corridor (no whole-city scans).
- Max 4 candidate routes.

### Assumptions

- A routing provider endpoint is reachable (default public OSRM; self-host later).
- Road imagery for tested routes is obtainable from the configured image source.
- Annotated dataset exists or will be prepared under `ml/dataset` with `data.yaml`.
- LLM API key may or may not be present; fallback explanation always works.

---

## 12. Delivery / Roadmap Alignment

Aligned to `00_MASTER_RULES.md` §42:

```
Phase 1  Foundation
Phase 2  Routing (up to 4 routes)
Phase 3  Road image pipeline
Phase 4  OpenCV preprocessing
Phase 5  YOLO11 dataset/training/inference
Phase 6  Hazard aggregation
Phase 7  Risk scoring
Phase 8  Facility intelligence
Phase 9  Route profile
Phase 10 LLM explanation
Phase 11 Testing
Phase 12 Security/performance/hardening
```

Each phase's Definition of Done is defined in `03_ARCHITECTURE.md` §11.

---

## 13. Related Documents

- `00_MASTER_RULES.md` — governing rules and boundaries
- `02_TRD.md` — technical requirements
- `03_ARCHITECTURE.md` — system architecture + build phases
- `04_DATA_MODEL.md` — entities
- `07_API_CONTRACT.md` — endpoints
- `13_TESTING.md` — test plan
- `14_PRODUCTION_CHECKLIST.md` — release gate