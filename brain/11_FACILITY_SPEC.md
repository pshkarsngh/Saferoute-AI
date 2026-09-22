# 11_FACILITY_SPEC.md — SafeRoute AI Facility Intelligence Specification

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Facility Intelligence Specification (corridor search, provider abstraction, categories, distance semantics, failure/zero handling)
**Version:** v1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_RULES.md` > `01_PRD.md` > `02_TRD.md` > `03_ARCHITECTURE.md` > `04_DATA_MODEL.md` > `07_API_CONTRACT.md` > this document
**Companion:** `04_DATA_MODEL.md` §7.17–§7.20 (persistence), `07_API_CONTRACT.md` §7.13–§7.14 (wire format), `02_TRD.md` §36–§42 & §93, `09_ERROR_HANDLING.md` §10.7, `13_TESTING.md`

---

## 1. POSITION OF THE FACILITY ENGINE

The Facility Engine is an **independent discovery stage** in the SafeRoute AI pipeline:

```
ROUTE GEOMETRY → CORRIDOR → SEARCH → NORMALIZE → DEDUP → DISTANCE → CATEGORIZE → AGGREGATE → ROUTE PROFILE
```

It is:

- **Separated from the Hazard/Risk Engine** (`02_TRD.md` §36). Facility counts never enter the risk score; risk never enters facility counts.
- **Route-corridor-scoped** — facilities are only those within a configurable distance of the route geometry, never a whole-city search (`MASTER_RULES.md` §15, `02_TRD.md` §38, `03_ARCHITECTURE.md` §6.8).
- **Provider-driven, data-source-honest** — it reports what a real provider returns. It never invents facilities, names, phones, opening hours, or distances (`MASTER_RULES.md` §23).
- **Failure-isolated** — a facility outage degrades only the facility domain (`02_TRD.md` §140–§141).

---

## 2. SEPARATE DIMENSIONS RULE (NEVER MERGED)

Facilities belong to two consumer dimensions and are **never** combined with road safety into one opaque score (`MASTER_RULES.md` §14, `03_ARCHITECTURE.md` §6.9, `02_TRD.md` §168):

| Dimension | Categories | Consumer question |
|-----------|-----------|-------------------|
| **Emergency Accessibility** | `hospital`, `medical_store`, `police_station` | "How reachable is urgent help?" |
| **Travel Convenience** | `restaurant`, `hotel`, `petrol_pump` | "How convenient is the journey?" |
| **Road Safety (never merged with these)** | hazard-derived `risk_score`, counts, density | handled entirely by the Risk Engine (`10_RISK_ENGINE.md`) |

Hard rules:

- More restaurants/hotels ≠ safer road (`03_ARCHITECTURE.md` §6.9).
- No `"Overall Safety Score"` is ever formed from facilities + hazards (`02_TRD.md` §168).
- The Route Profile carries safety, emergency accessibility, and convenience as sibling, independent blocks (§12; `03_ARCHITECTURE.md` §6.9).

---

## 3. CATEGORY MODEL

### 3.1 Canonical category enum (v1)

```
hospital
medical_store
restaurant
hotel
petrol_pump
police_station
```

- One normalized `Facility` table driven by a `category` column — **never** one table per category (`04_DATA_MODEL.md` §7.18).
- Each category maps to provider query tags (see §6).
- Unknown category in an API request → `422 VALIDATION_ERROR` (`07_API_CONTRACT.md` §7.13).

### 3.2 Extensibility (future categories)

Accepted as enum/gating table values *only when they support the product scope* (`MASTER_RULES.md` §4/§15, `04_DATA_MODEL.md` §7.18):

```
ev_charging        (road-trip feasibility)
fire_station       (emergency accessibility)
atm                (travel convenience)
parking            (travel convenience)
repair             (travel convenience / emergency fallback)
tire_shop          (travel convenience / emergency fallback)
emergency_services (emergency accessibility)
```

- A new category requires: PRD/TRD scope check → mapping to provider tags → tests → a `configuration_version` note. Never add a category "because it is cool".
- Facility Engine treats categories as **config-driven**; the search and aggregation code is category-agnostic (`03_ARCHITECTURE.md` §6.8).

---

## 4. CORRIDOR SEARCH ALGORITHM

Default algorithm — evaluated in this exact order:

```
ROUTE GEOMETRY (authoritative normalized polyline)
   ↓ 1. SAMPLING
   build route points from geometry (decimate to ≤ ~200m spacing, keep all vertices)
   ↓ 2. CORRIDOR
   corridor radius R = FACILITY_SEARCH_RADIUS_KM (default 1.0 km; config)
   envelope   = bounding box of route points expanded by R in all directions
   ↓ 3. PROVIDER QUERY (per category)
   query provider for category within `envelope` (bbox / around in provider terms)
   results = provider_response (may be empty or failed)
   ↓ 4. NORMALIZE
   map provider element → internal Facility schema (ProviderSource, provider_facility_id, name, category, lat/lon, address?, phone?, opening_status?, metadata)
   drop records with missing/invalid coordinates or unknown category
   ↓ 5. DEDUP
   collapse repeats (see §9)
   ↓ 6. DISTANCE CALC
   compute distance metric for each unique facility (§10)
   ↓ 7. CORRIDOR FILTER (exact)
   keep facilities with distance(point→polyline) ≤ R   ← removes bbox corners/outliers
   ↓ 8. CATEGORIZE
   tag each kept facility to its canonical category (already assigned)
   ↓ 9. AGGREGATE
   per-category: count + nearest_distance (+ cached list for GET /facilities)
   ↓ 10. PERSIST
   associate route ⇄ facility (route_facilities) with distance_metric, nearest_segment, search_radius, provider
   ↓ 11. OUTPUT
   summary (§12) into Route Profile + facilities list into API §7.13
```

Notes:

- The bbox is a **coarse pre-filter**; the corridor filter (§7) is the authoritative "inside radius" test. A facility inside the bbox corner but farther than R from the route is excluded.
- `MAX_FACILITY_RESULTS` caps total kept facilities per category; the cap is configurable and logged when hit.
- If the route has no usable geometry → the facility domain is `unavailable` (`route_geometry_invalid`), never an empty `[]` that implies "no facilities" (`02_TRD.md` §137).

---

## 5. PROVIDER ABSTRACTION

All external facility data flows through one internal interface (`02_TRD.md` §93). No provider-specific code leaks into services:

```
FacilityProvider
  ├── search(query)        → raw provider results for a category in a region/envelope
  ├── normalize(raw)       → internal Facility records (validated)
  └── health_check()       → availability probe (timeout-bounded, cached)
```

| Method | Contract | Failure behavior |
|--------|----------|------------------|
| `search()` | takes corridor envelope (bbox + center points) + category + radius + result caps | raises typed `FacilityProviderError` (timeout / 429 / 5xx); the engine converts to `unavailable`, never empty success |
| `normalize()` | validates fields; drops invalid rows with per-row log (`FACILITY_DROP_INVALID`) | malformed payload → provider-level failure |
| `health_check()` | bounded HTTP probe; result cached ~60s | false/error ⇒ `health=false`, facility domain `unavailable` on subsequent searches until provider recovers |

- **Default provider:** Overpass API (OpenStreetMap), keyless (`03_ARCHITECTURE.md` §2). Swappable via `FACILITY_PROVIDER` config.
- Provider name + source are stored on every facility row / association (`04_DATA_MODEL.md` §7.17, §7.19) for traceability (`02_TRD.md` §133).

---

## 6. OVERPASS DEFAULT PROVIDER

- Endpoint: `OVERPASS_BASE_URL` (default `https://overpass-api.de/api/interpreter`).
- Query style per category (tags; exact set config-driven):

| category | OSM tag basis (default) |
|----------|-------------------------|
| `hospital` | `amenity=hospital` |
| `medical_store` | `amenity=pharmacy` (`medical_store`) |
| `police_station` | `amenity=police` |
| `restaurant` | `amenity=restaurant` |
| `hotel` | `tourism=hotel` (consult config for motel/guest_house expansion) |
| `petrol_pump` | `amenity=fuel` |

- Use `[out:json][timeout:N]` with `N = FACILITY_QUERY_TIMEOUT_S` (default 30 s).
- Query the **route corridor envelope** (bbox expanded by radius), then the exact interval filter from §4.
- Prefer element types: `node`, `way` centroid, `relation` centroid — normalized the same way.
- Respect public-instance etiquette: keep request rate low, send a descriptive `User-Agent`, honor `Retry-After` (see §16). Prefer self-hosted Overpass for production load.

---

## 7. NORMALIZATION

Provider element → internal `Facility` (validated against adverse schema; `02_TRD.md` §116–§117):

```
facility_id          → assigned server-side (uuid)
provider             → config provider name, e.g. 'overpass'
provider_facility_id → provider's numeric id (preferred dedup key)
name                 → element name tag; MISSING → 'Unnamed <category>' (never fabricate a name)
category             → canonical enum (§3)
latitude/longitude   → centroid (node = point; way/relation = centroid)
address|phone|opening_status → copied only when the provider actually supplies them;
                               otherwise null (MASTER_RULES.md §23)
metadata             → jsonb original provider extras (excluded from LLM by default)
first_seen_at/last_seen_at → discovery timestamps
```

**Never** fabricate: names, phone numbers, addresses, opening hours, ratings, or availability (`MASTER_PROJECT_PROMPT.md` §24). Unavailable fields stay `null`.

---

## 8. QUERY & RESULT LIMITS

- `MAX_FACILITY_RESULTS` (default 200 per category) caps aggregation; excess dropped with a log counter.
- `FACILITY_QUERY_TIMEOUT_S` bounds each provider call (`02_TRD.md` §98).
- Results are **cached** (see §15) to avoid repeated cost; the cache carries the radius + provider in the key.

---

## 9. DEDUPLICATION

Providers may return the same place multiple times (duplicate nodes, way+node overlap, bbox overlap when chunking). Dedup order:

1. **Provider ID** — authoritative when present: same `provider_facility_id` ⇒ duplicate.
2. **Coordinates** — within `FACILITY_DEDUP_DISTANCE_M` (default 30 m) ⇒ duplicate (unless provider ID already resolved them differently).
3. **Name + address** — residual fallback: normalized name (lowercase, trimmed, whitespace-collapsed) AND normalized address both equal ⇒ duplicate.

- Keep the first occurrence; keep the richer record if one has address/phone and the other does not.
- Dedup happens **per route** (a facility is a unique row globally; association rows are per route). `UNIQUE(route_id, facility_id)` (`04_DATA_MODEL.md` §7.19).
- Tests: N duplicate provider records → 1 unique facility (`02_TRD.md` §111).

---

## 10. DISTANCE SEMANTICS

Distance is always **route-relative** and the metric is always explicit and persisted (`04_DATA_MODEL.md` §7.19–§7.20; `07_API_CONTRACT.md` §7.13 — `distance_metric` is mandatory).

| `distance_metric` | Definition | Default? | Persisted unit |
|-------------------|-----------|----------|----------------|
| `straight_line` | Great-circle (haversine) distance from the facility point to the **nearest point on the route polyline** (point-to-polyline). | **Yes (v1)** | km in DB, meters in API |
| `to_nearest_segment` | Distance from the facility point to the **nearest route segment's geometry**; `nearest_segment_id` recorded alongside. | No | km in DB |
| `driving` | Road-network driving distance, **only** if a driving-distance source is available. Not available from Overpass in v1. | No | km in DB |

Hard rules:

- **Never** label `straight_line` (point-to-polyline) as "driving distance" (`04_DATA_MODEL.md` §7.20, `02_TRD.md` §40).
- Output field name matches the metric: `distance_from_route_meters` for `straight_line`, etc. (`07_API_CONTRACT.md` §7.13).
- If a facility cannot be matched to a polyline point (no geometry) → exclude it; never guess a distance.
- Haversine, deterministic; same coordinates ⇒ same distance (reproducibility, `02_TRD.md` §65).

---

## 11. CATEGORIZATION

- Category is assigned during normalization from the provider tag mapping (§6), not after distance.
- Aggregation is per canonical category (§3.1). A facility belongs to exactly one category per query (multi-tag entries resolve to the configured primary mapping).
- Route Profile and API expose categories under their dimension group (§2, §12) — the grouping is presentational; the numeric data is per-category.

---

## 12. AGGREGATION & SUMMARY OUTPUT

Internal summary per route-category (persisted via `route_facilities` + `RouteAnalysis.facility_status/count`, `04_DATA_MODEL.md` §7.19, §7.21):

```
{
  "category": "hospital",
  "count": 3,
  "nearest_distance_meters": 800,
  "nearest_facility_id": "facility_1",
  "status": "completed"            // 'completed' | 'unavailable'
}
```

Canonical wire shape per `07_API_CONTRACT.md` §7.14:

```json
{
  "route_id": "route_1",
  "status": "completed",
  "hospitals":     { "count": 3, "nearest_distance_meters": 800 },
  "medical_stores":{"count": 7, "nearest_distance_meters": 200 },
  "restaurants":   { "count": 15, "nearest_distance_meters": 100 },
  "hotels":        { "count": 5,  "nearest_distance_meters": 600 },
  "petrol_pumps":  { "count": 2,  "nearest_distance_meters": 900 },
  "police_stations":{"count": 1,  "nearest_distance_meters": 1200 }
}
```

Route Profile merges this under two dimensions (§2) without inventing a merged number (`03_ARCHITECTURE.md` §6.10).

---

## 13. ZERO VS UNAVAILABLE (MANDATORY)

This is a strict boundary (`MASTER_PROJECT_PROMPT.md` §26, `02_TRD.md` §137, `09_ERROR_HANDLING.md` §10.7, `07_API_CONTRACT.md` §7.14):

| Provider outcome | Correct output | Never output |
|------------------|----------------|--------------|
| Successful search, zero matches | `"count": 0` with `status: "completed"` — "0 hospitals found in corridor" | silently omitting the category |
| Successful search, N matches | `"count": N` + nearest distance | — |
| Provider timeout / 5xx / network fail | `{ "status": "unavailable" }` (domain or per-category) | `"count": 0` (converts failure into zero) |
| Route geometry invalid | `{ "status": "unavailable", "reason": "route_geometry_invalid" }` | `[]` implying "no facilities" |

Rules:

- `count: 0` ⇒ "zero after a **successful** search".
- `unavailable` ⇒ "provider/geometry made discovery impossible".
- The UI renders the two states **visually distinctly** (`09_ERROR_HANDLING.md` §10.7, `08_UI_SPEC.md` §14.6).
- An `unavailable` facility domain never fabricates values (`MASTER_RULES.md` §22).

---

## 14. FAILURE / ISOLATION

- Facility failure affects **only** the facility domain: `RouteAnalysis.facility_status = 'unavailable'`, `facility_count = 0`-as-unavailable-qualified or excluded, route + safety + risk remain intact (`02_TRD.md` §140–§141; `09_ERROR_HANDLING.md` §10.7; `04_DATA_MODEL.md` §7.21).
- Partial failure model: per-request the engine may report per-category status; v1 default is domain-level `status` (`07_API_CONTRACT.md` §7.14). Never fabricate facilities to "fill" a category.
- A provider returning an element with no coordinates or unknown category is dropped with a log, not treated as a failure and not counted.
- Retroactive isolation: cached facility data is only reused if its `(geometry hash, category, radius, provider)` key still matches (§15).

---

## 15. CACHING KEYS

Cache facility results per the cache rules (`MASTER_RULES.md` §33, `02_TRD.md` §85). A single caching namespace keyed by:

```
sha256 of ( canonical route geometry polyline           # sorted/generated from authoritative normalized geometry
           + category
           + FACILITY_SEARCH_RADIUS_KM
           + provider name (e.g. 'overpass')
           + facility config version )                  # tag mapping / category set version
```

- Geometry hash input is the **same normalized polyline** the Risk Engine uses (deterministic serialization; coordinates to 6 decimals).
- Any of the five components changing ⇒ cache miss, fresh search.
- TTL: `FACILITY_CACHE_TTL_S` (default 3600 s). Respect provider terms; never cache sensitive user data indefinitely (`02_TRD.md` §52).
- Cached entries must be labeled as cached in logs; never present stale facility data as live (`MASTER_PROJECT_PROMPT.md` §61).

---

## 16. RATE LIMIT & RETRY POLITENESS

Matches the global retry matrix (`09_ERROR_HANDLING.md` §11.1, `02_TRD.md` §96–§97):

- **Retryable:** transient network error, timeout, provider 5xx — max 3 attempts, exponential backoff with jitter, honoring `Retry-After`.
- **Never retry:** 4xx (invalid request/area), invalid coordinates, security violations.
- **429 handling:** back off per `Retry-After`, fall back to cache if present, else `unavailable`; count in `facility_requests_total`/`facility_failures` (`02_TRD.md` §159).
- **Politeness:** all searches are reads; batch categories per request where the provider supports multiple tags; dedupe overlapping bboxes; respect public Overpass instance guidelines (rate, User-Agent, off-peak).
- **Caching first:** repeated identical route searches hit cache before hitting the provider.

---

## 17. CONFIGURATION SUMMARY

| Variable | Default | Purpose |
|----------|---------|---------|
| `FACILITY_PROVIDER` | `overpass` | active provider |
| `OVERPASS_BASE_URL` | `https://overpass-api.de/api/interpreter` | provider endpoint |
| `FACILITY_SEARCH_RADIUS_KM` | `1.0` | corridor radius (route buffer) |
| `FACILITY_QUERY_TIMEOUT_S` | `30` | per-query timeout |
| `MAX_FACILITY_RESULTS` | `200` | per-category cap |
| `FACILITY_DEDUP_DISTANCE_M` | `30` | coordinate dedup distance |
| `FACILITY_CACHE_TTL_S` | `3600` | cache TTL |
| `FACILITY_CATEGORIES` | the six v1 categories | active category set |

---

## 18. CONSISTENCY & LIMITATIONS

- Consistent with `04_DATA_MODEL.md` §7.17–§7.20 (one `Facility` table, category column, `RouteFacility` distance semantics), `07_API_CONTRACT.md` §7.13–§7.14 (meters, explicit `distance_metric`, zero-vs-unavailable), and `02_TRD.md` §38–§42 (corridor, dedup, distance, failure).
- Limitations: provider coverage/absence is a real-world ceiling (`02_TRD.md` §137); do not claim "no hospitals nearby" when the provider merely returned nothing post-error; opening status is only what the provider supplies and may be stale (`MASTER_PROJECT_PROMPT.md` §60).

---

# END OF FACILITY INTELLIGENCE SPECIFICATION