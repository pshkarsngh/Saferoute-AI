# 19_REAL_WORLD_OPERATION.md — Real-World Operation Specification

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Real-World Operation Specification (request lifecycles, failure behavior, degraded states)
**Version:** 1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_RULES.md` > `MASTER_PROJECT_PROMPT.md` > `01_PRD.md` > `02_TRD.md` > `03_ARCHITECTURE.md` > this document
**Companion:** `09_ERROR_HANDLING.md` (error taxonomy & retry policy), `07_API_CONTRACT.md` (endpoint contract), `08_UI_SPEC.md` (frontend states), `06_AI_SOURCES.md`, `20_LIMITATIONS_AND_ASSUMPTIONS.md`

This document defines how SafeRoute AI behaves in the real world: the exact lifecycle of a live request from a person typing two locations through to a route decision, what happens at every stage, and precisely what the system does — and what the user sees — when imagery, YOLO11, a facility provider, the routing provider, the database, or the LLM fails.

It exists to prove the system is designed for real operational conditions, not just a college demo.

---

## 1. OPERATING CONTEXT

### 1.1 What runs in production

```
USER WEB BROWSER
   │
   ▼
FRONTEND (React + Vite + TypeScript, react-leaflet)
   │  public API only, no provider keys
   ▼
BACKEND API (FastAPI, /api/v1)
   │
   ├── Routing Service ─────────────► OSRM public API (keyless)
   ├── Facility Service ────────────► Overpass API (OpenStreetMap)
   ├── Vision Pipeline ─────────────► OpenCV preprocessing → YOLO11 (MODEL_PATH)
   ├── Risk Engine (deterministic, versioned)
   ├── Route Profile Engine
   ├── LLM Service ─────────────────► OpenAI-compatible chat-completions
   ├── Database (PostgreSQL) + Cache (in-memory v1)
   └── Structured Logger + Metrics
```

### 1.2 The nine responsibilities (never merged)

```
ROUTING       generates candidate routes (1–4)
OPENCV        preprocesses imagery
YOLO11        detects trained hazard classes
HAZARD ENGINE aggregates image detections into unique hazards
RISK ENGINE   calculates the deterministic 0–100 project metric
FACILITY ENGINE finds facilities inside the route corridor
ROUTE PROFILE combines only verified structured information
LLM           explains the verified information (grounded, never authoritative)
FRONTEND      presents evidence; the user makes the final decision
```

### 1.3 Ground truth rules that apply to every real request

- Only evidence actually produced by the system or a validated provider reaches the user.
- A subsystem that fails does not destroy the parts of the analysis that succeeded.
- "Unavailable" is never presented as "zero"; a failed analysis is never presented as a successful one.
- No subsystem silently takes over another subsystem's responsibility.

---

## 2. THE COMPLETE REAL REQUEST LIFECYCLE

### 2.1 Stage 0 — App open

The user opens the frontend. The frontend renders the landing page and initializes the map. Nothing is queried until the user acts.

What the user sees: landing page, source input, destination input.
What must NOT happen: any provider key in the browser, any automatic route analysis, fake progress.

### 2.2 Stage 1 — User enters source and destination

The user types (or autocompletes) a source and destination, e.g.:

- Source: `Alva's Institute of Engineering and Technology`
- Destination: `Mangaluru Railway Station`

The frontend runs client-side validation:
- source and destination both present
- source ≠ destination (warn if identical)
- coordinates, if any, are within lat [-90,90], lon [-180,180]

If validation fails, inline field errors appear. Nothing is sent.

### 2.3 Stage 2 — Route request (`POST /api/v1/route-requests`)

The frontend sends:

```json
{
  "source": { "latitude": 12.97, "longitude": 74.88, "name": "Alva's Institute of Engineering and Technology" },
  "destination": { "latitude": 12.91, "longitude": 74.85, "name": "Mangaluru Railway Station" }
}
```

Backend behavior, in order:

1. Schema-validate the request (Pydantic), re-validate coordinate ranges, reject unknown fields.
2. Generate a `request_id` (or honor `X-Request-ID`) — this value flows through every downstream log, error, and response.
3. Call the configured `RoutingService` → OSRM `/route/v1/driving/{lon},{lat};{lon},{lat}?alternatives=true&steps=false`.
4. Parse and **schema-validate** the provider response at the adapter boundary.
5. Normalize each returned route into the internal model: `route_id, sequence, distance_meters, duration_seconds, geometry (GeoJSON LineString [lon,lat]), segments, provider, provider_route_id`.
6. Create at most `MAX_CANDIDATE_ROUTES` (default 4) routes. **The actual count is whatever the provider returned, 1–4. Never padded.**
7. Persist `route_request` + `routes` + `route_segments` in one transaction.
8. Return `201` with the candidate routes.

What the user sees: up to four route cards + their polylines on the map, each with distance and duration.

Failure at this stage → see §3.1.

### 2.4 Stage 3 — Route segmentation

Segmentation strategy (documented, fixed): each route is split into segments of `SEGMENT_LENGTH_METERS` (default 500 m) along the route geometry, preserving order via `sequence`. The last partial segment is kept. Segmentation exists so imagery and hazards are tied to the smallest practical geographic unit.

- Segment order is preserved; `UNIQUE(route_id, sequence)`.
- Segmentation rules are documented and not silently changed.

### 2.5 Stage 4 — Road imagery collection

For each route (processed independently, in parallel where safe), the image pipeline:

1. For each segment, queries the configured imagery source for road imagery near the segment.
2. Validates each candidate image: existence, MIME, size (`IMAGE_MAX_SIZE`), decode, dimensions, content.
3. Records metadata: `image_id, route_id, segment_id, source, latitude, longitude, captured_at?, collected_at, image_hash, processing_status`.
4. Stores image bytes in object/disk storage; the database stores only the reference + hash.

**Real-world truth:** imagery is NOT assumed to exist for every road. Each segment ends in exactly one state: imagery available / partial / unavailable / collection failed.

What the user sees: analysis progress shows "Collecting road imagery…" with real stages, never fake percentages.

Failure at this stage → see §3.3.

### 2.6 Stage 5 — OpenCV preprocessing

Each valid image passes through the OpenCV pipeline:

```
Read → Validate → Resize (model input size) → Color conversion → Optional noise reduction
→ Optional contrast enhancement → Normalization → YOLO11 input
```

OpenCV also performs quality checks (resolution, blur, exposure, corruption). Low-quality images are marked `low_quality`/`corrupt` and **excluded from inference**, with the reason recorded in `ImageProcessingResult`.

OpenCV = preprocessing only. It never "detects potholes".

Failure at this stage → see §3.4.

### 2.7 Stage 6 — YOLO11 inference

1. The model is loaded once per process (`MODEL_PATH`), not per image.
2. Each preprocessed image is inferred against the active `ModelVersion`.
3. Detections below `CONFIDENCE_THRESHOLD` are discarded.
4. Each kept detection is a `HazardDetection` row: `class_id, hazard_type (from data.yaml only), confidence, bounding_box, image_id, route_id, segment_id, latitude?, longitude?, model_version_id, inference_timestamp`.

Real-world semantics:
- A detection is a prediction in one image — **not** automatically a unique real-world hazard.
- Detection confidence (e.g. 91%) is detector confidence, not "91% road danger".

Failure at this stage → see §3.5.

### 2.8 Stage 7 — Hazard aggregation

Aggregation converts image-level detections into route-level hazard facts:

```
YOLO detections → validate → duplicate handling → spatial clustering → unique Hazard → route summary
```

Duplicates: the same physical pothole photographed in 5 overlapping images must not count as 5 potholes. Clustering uses geographic proximity (`CLUSTER_RADIUS_M`), segment association, image overlap, and class. Each member detection is linked to the aggregated `Hazard`; `detection_count` and `confidence_summary` record the aggregation.

Output example (route summary):

```json
{ "potholes": 3, "road_cracks": 2, "damaged_roads": 1, "obstacles": 1, "debris": 0 }
```

Only genuinely aggregated hazards appear. Unanalyzed segments contribute nothing — they must never be reported as "no hazards".

### 2.9 Stage 8 — Risk calculation

The risk engine computes a **deterministic** 0–100 metric from the aggregated hazards and route exposure (see `10_RISK_ENGINE.md` for the exact, versioned formula). It records `risk_analysis` with `algorithm_version`, `configuration_version`, `weighted_components`, and `status` (`calculated` | `unavailable`).

- Same input + same config + same model output ⇒ same risk score. Reproducible.
- The LLM never touches this score.
- On missing risk input, `status = unavailable` — never a fake `score = 0`.

### 2.10 Stage 9 — Facility discovery

The facility engine searches **only inside the route corridor** (`FACILITY_SEARCH_RADIUS_KM`), for six categories:

- Emergency Accessibility: `hospital`, `medical_store`, `police_station`
- Travel Convenience: `restaurant`, `hotel`, `petrol_pump`

Pipeline: route geometry → corridor/bbox → Overpass query → schema-validate → normalize → dedup → compute distance (point-to-polyline, explicit `distance_metric`) → categorize → aggregate counts + nearest distance.

Real-world semantics:
- `count: 0` means a *successful* search found nothing.
- Provider failure means `{"status": "unavailable"}` — never `0`.
- Straight-line distance is never mislabeled as driving distance.
- Facility data never merges into the risk score; more restaurants ≠ safer road.

Failure at this stage → see §3.6.

### 2.11 Stage 10 — Route profile

The Route Profile Engine combines only verified data into the canonical profile:

```
route (distance, duration, geometry, segments)
+ safety (risk, hazards, images_analyzed, segments_analyzed, status)
+ facilities (per-category count + nearest distance, status)
+ analysis (status: pending/processing/completed/partial/failed)
```

Domains stay separate. There is **no** combined "Overall AI Score".

### 2.12 Stage 11 — LLM explanation

The LLM service receives **only** the structured Route Profile (referenced by `route_analysis_id` — the client never submits authoritative numbers). It produces a grounded natural-language explanation under hard grounding rules, then the output is validated before display.

- LLM failure or missing key → deterministic fallback sentence built from the profile, `fallback: true`. The structured analysis is unaffected.
- LLM output is untrusted text: rendered as plain text / sanitized markdown in the frontend, never raw HTML.

### 2.13 Stage 12 — Frontend rendering & user decision

The frontend renders: map (source, destination, routes, selected-route emphasis, hazard markers, facility markers, legend, filters), route cards, safety dashboard (risk always shown as `28 / 100`, never color alone, never "safe"), facility summary (emergency accessibility and travel convenience separated), and the AI explanation clearly labeled and visually subordinate to the structured data.

The user reviews the evidence and chooses. The system never declares a universal winner.

---

## 3. WHAT HAPPENS WHEN SOMETHING FAILS (REAL OPERATING CONDITIONS)

This section is the operational core: for each failure, what is detected, what the system does, and exactly what the user sees.

The universal rule (from `09_ERROR_HANDLING.md`): **Detect → Classify → Log → Return explicit status.** Never: fail → invent a result.

### 3.1 Routing provider failure / no route

- Detection: HTTP non-2xx, schema-validation failure, timeout, or empty route table.
- Retry: transient only (5xx/timeout), bounded exponential backoff (max 3); never on 4xx or invalid coordinates.
- Behavior:
  - If ≥1 route is valid → return the valid ones (partial), set per-route status.
  - If all fail → `404 NO_ROUTE_FOUND` or `502 ROUTING_PROVIDER_ERROR` envelope.
- User sees:
  - No routes: "No routes were found for the selected locations." (with Retry / Edit locations)
  - Provider down: "Unable to generate routes right now."
- Never: fabricated routes to reach 4, LLM-invented routes, `distance 0`.

### 3.2 Invalid source / destination

- Backend validation rejects out-of-range or malformed coordinates with `422 INVALID_COORDINATES` / `VALIDATION_ERROR`.
- User sees inline field messages ("Please enter a valid source location.").
- Huge or malformed payloads → `413`/`400`; never a stack trace.

### 3.3 Imagery unavailable (partial or full)

- Each segment is marked with its own imagery state. Available imagery proceeds; missing imagery is skipped as "non-analyzed".
- If imagery is unavailable for a section, the system **never** reports "no hazards detected" for it.
- User sees: "Road imagery is unavailable for part of this route."
- Logged as `IMAGE_UNAVAILABLE` (WARNING); the route still works.

### 3.4 OpenCV / image-processing failure

- A corrupt/unreadable/unsupported image is marked `invalid` (or `low_quality`/`corrupt`) with the reason stored in `ImageProcessingResult`; it is excluded from inference.
- User impact: none directly (fewer analyzed images). `images_analyzed` reflects the true number.
- Logged as `OPENCV_PROCESSING_FAILED` (WARNING).

### 3.5 YOLO11 / model failure

- Transient per-image error → one bounded retry, then skip that image.
- Model load failure, corrupt artifact, or version mismatch → the safety stage becomes `unavailable`. Route info and facilities are still returned.
- Detection rows lacking model-version provenance are rejected (never counted).
- User sees: safety section shows "Road hazard analysis is unavailable for this route." (never `risk: 0`, never "no hazards")
- Logged as `YOLO_INFERENCE_FAILED` / `MODEL_LOAD_FAILED` (ERROR/CRITICAL) with `model_version`.

### 3.6 Facility provider failure (and zero vs unavailable)

- Provider down / malformed response → facility domain `{"status": "unavailable"}`; route + safety unaffected.
- Successful search, zero results → `count: 0`.
- User sees:
  - Unavailable: "Facility information is currently unavailable."
  - Zero: "0 hospitals found."
- Logged as `FACILITY_PROVIDER_ERROR` (WARNING/ERROR).

### 3.7 LLM failure / missing key

- Provider error or timeout → max 1 retry → deterministic fallback text (`fallback: true`).
- No key configured → same fallback (feature degrades gracefully).
- The structured analysis (risk, hazards, facilities, route) is always returned.
- User sees: "AI explanation is currently unavailable." — the evidence panels remain fully usable.
- Logged as `LLM_PROVIDER_ERROR` (WARNING).

### 3.8 Database failure

- Connection errors → bounded backoff with connection pooling; a critical persistence failure fails the request explicitly with `DATABASE_ERROR` (no phantom partial records; the request/side-effect transaction rolls back).
- Migrations are versioned; a migration failure follows `runbooks/database-migration-failure.md`.
- User sees: generic error envelope; `request_id` available for support.

### 3.9 Timeouts & rate limits

- Every external call has `REQUEST_TIMEOUT`; analysis timeout → `504 ANALYSIS_TIMEOUT` or the async job continues and the frontend polls `GET /api/v1/jobs/{job_id}`.
- Provider 429 → respect `Retry-After`, bounded backoff, cache reuse; our API rate-limits expensive endpoints → `429 RATE_LIMITED` + `Retry-After`.
- User sees: clear messages, no hanging spinners.

### 3.10 Network / offline

- Live calls fail → frontend shows an actionable error ("Unable to retrieve route.") and, where appropriate, clearly labeled cached data — never stale data presented as live.
- Security/malicious input → rejected, never executed, logged, alerted. Fail closed.

---

## 4. DEGRADED-STATE MATRIX (what the user sees, per subsystem)

| Scenario | Route | Distance/Duration | Risk/Hazards | Facilities | AI explanation |
|----------|-------|-------------------|--------------|------------|----------------|
| All healthy | ✓ | ✓ | ✓ 28/100 | ✓ counts | ✓ grounded |
| Imagery partial | ✓ | ✓ | ✓ but fewer images | ✓ | ✓ (mentions partial) |
| YOLO down | ✓ | ✓ | ✗ "unavailable" | ✓ | ✓ (or fallback) |
| Facility provider down | ✓ | ✓ | ✓ | ✗ "unavailable" | ✓ fallback |
| LLM down / no key | ✓ | ✓ | ✓ | ✓ | ✗ fallback text |
| Routing down | ✗ error | — | — | — | — |
| DB down | ✗ explicit error | — | — | — | — |

Requirements:
- A failing optional subsystem never hides the route or the data that succeeded.
- "Unavailable" states are visually distinct from "zero" and from "not analyzed".

---

## 5. CACHING & BACKGROUND RE-ANALYSIS (the real-life difference)

A real system does not re-analyze every image on every search:

1. `POST /api/v1/route-requests` checks for a recent analysis (cache key = geometry hash + provider + config + model version + radius).
2. Valid recent analysis → reused, latency/cost saved.
3. Stale analysis → background re-analysis; the user may see the previous result labeled as cached, or a progress state.

Cache rules:
- Cache keys always include model version + configuration (a model change invalidates results).
- No sensitive user data cached indefinitely; provider terms and freshness respected.
- Cache is a cache — never presented as fresh live data.

---

## 6. ASYNC ANALYSIS OPERATION

When analysis exceeds a synchronous cost threshold, it runs as a job:

```
POST /api/v1/routes/{route_id}/analysis  →  202 { job_id, route_id, status: queued }
Frontend polls GET /api/v1/jobs/{job_id}
Stages: ROUTE_GENERATION → IMAGE_COLLECTION → IMAGE_VALIDATION → OPENCV_PREPROCESSING
       → YOLO_INFERENCE → HAZARD_AGGREGATION → RISK_CALCULATION → FACILITY_ANALYSIS
       → ROUTE_PROFILE → LLM_EXPLANATION → COMPLETED
```

- The UI shows real stages (`✓ Route generated`, `● Hazard detection`, …), never invented percentages.
- A job can complete as `partial` (some subsystem unavailable) and still return its valid domains.
- v1 uses FastAPI `BackgroundTasks`/asyncio; no Celery or message queue unless a measured workload requires it (`17_DECISIONS.md` ADR-003).

---

## 7. OBSERVABILITY DURING OPERATION

For every request the system records (never secrets):

`ts, level, service, request_id, route_id, job_id, stage, duration_ms, error_code, error_type, provider, status, model_version, configuration_version`

Outcome statuses: `succeeded | partial | failed | unavailable | cancelled | timed_out`.

Operational metrics: route_requests_total, route_generation_failures, analysis_requests_total/failures, yolo_inference_count/duration, facility_requests_total/failures, llm_requests_total/failures, average_analysis_duration, error_rate by code, partial_analysis_count, cache hit rate.

Alerting: model-load/DB failure paged; sustained provider failure warned; `INTERNAL_ERROR`/`SECURITY_VIOLATION` spikes alert + incident runbook. Full detail in `16_MONITORING.md`.

Incident diagnosis: find `request_id` → trace stages via logs → distinguish app bug vs provider outage vs config/model issue (using the degraded-state matrix above) → apply smallest correct fix → rerun error-path tests → update docs if behavior changed.

---

## 8. OPERATIONAL GUARANTEES (recap)

- Every number the user sees was computed or retrieved by a real component — never invented.
- Route geometry is authoritative routing output; the LLM never modifies it.
- The risk score is deterministic, versioned, and reproducible; the LLM never computes or changes it.
- Safety, emergency accessibility, and convenience stay in separate dimensions.
- Unavailable ≠ zero, failed ≠ successful, not-analyzed ≠ no-hazards, straight-line ≠ driving distance.
- A user can always see the evidence and remains the final decision-maker.

---

## 9. RELATED DOCUMENTS

- `09_ERROR_HANDLING.md` — error taxonomy, retry/fallback matrix, error envelope
- `07_API_CONTRACT.md` — endpoint contracts, error codes, partial-success envelope
- `08_UI_SPEC.md` — how each degraded state is rendered
- `10_RISK_ENGINE.md` — the deterministic score the operation depends on
- `16_MONITORING.md` — metrics, logs, alerting used during real operation
- `20_LIMITATIONS_AND_ASSUMPTIONS.md` — what the system cannot guarantee
- `runbooks/` — incident procedures

---

# END OF REAL-WORLD OPERATION SPECIFICATION