# Data Sources — SafeRoute AI

Routing, road imagery, facilities, datasets, and LLM sources. Each data class has a distinct provider, purpose, and failure behavior.

## Principle

- Every value in the app traces to a configured provider or to the trained model — never invented (`MASTER_RULES.md` §23).
- Providers are isolated behind internal interfaces so they can be replaced (`TRD` §93–§95).
- All provider responses are schema-validated before entering the system (`TRD` §116–§117).

## Source Categories

### 1. Routing Provider (generates candidate routes)

| Property | Value |
|----------|-------|
| Default | OSRM public API (`ROUTING_BASE_URL`, keyless) |
| Responsibility | candidate routes, distance, duration, geometry, segments |
| Replacement | any provider implementing `RoutingProvider` (`geocode`, `route`, `normalize`) |
| Config | `ROUTING_PROVIDER`, `ROUTING_BASE_URL`, `MAX_CANDIDATE_ROUTES` |
| Failure | typed `ROUTING_PROVIDER_FAILURE`; no fabricated routes |

Rules:
- Returns up to 4 alternatives; fewer is valid — never pad to four.
- Provider-specific schema normalized once at the boundary (`TRD` §12).

### 2. Road Imagery Provider

| Property | Value |
|----------|-------|
| Default | configured imagery source (e.g. street-level imagery provider or permitted collection) |
| Responsibility | images per route segment, with geo metadata |
| Config | image source settings; `IMAGE_MAX_SIZE` |
| Failure | `IMAGE_UNAVAILABLE` / `INVALID_IMAGE`; segments without imagery are reported as non-analyzed, not as "no hazards" |

Rules:
- Metadata: `image_id, route_id, segment_id, lat, lon, source, timestamp, processing_status` (`TRD` §16).
- Only imagery the system is permitted to use may be collected (see `06_SCRAPING_SPEC.md`).

### 3. Facility Provider (nearby facilities)

| Property | Value |
|----------|-------|
| Default | Overpass API (OpenStreetMap, keyless) |
| Responsibility | facilities inside the route corridor |
| Config | `FACILITY_PROVIDER`, `OVERPASS_BASE_URL`, `FACILITY_SEARCH_RADIUS_KM` |
| Failure | `FACILITY_PROVIDER_FAILURE` → `facility_data_status=unavailable`; zero results ≠ provider failure (`TRD` §137) |

Categories (configurable):
`hospital`, `medical_store`, `restaurant`, `hotel`, `petrol_pump`, `police_station`
(extensible: ev_charging, fire_station, atm, parking, repair, tire_shop, emergency — only if they support the product).

### 4. YOLO11 Dataset & Model (hazards)

| Property | Value |
|----------|-------|
| Location | `ml/dataset` (images/labels train|val|test + `data.yaml`), `ml/models` (gitignored) |
| Sources | only permitted/annotated imagery with documented licensing |
| Classes | exactly those in `data.yaml` (e.g. `pothole`, `road_crack`, `damaged_road`, `obstacle`, `debris`) |
| Config | `MODEL_PATH`, `MODEL_NAME`, `MODEL_VERSION`, `CONFIDENCE_THRESHOLD`, `YOLO_IOU_THRESHOLD` |
| Documentation | `docs/AI_MODELS.md` — dataset source, annotation format, metrics (never fabricated) |

Rules:
- Training data separated from production inference (`TRD`; MASTER_RULES §9).
- Model version tracked on every detection (`TRD` §25).

### 5. LLM Provider (explanation only)

| Property | Value |
|----------|-------|
| Default | OpenAI-compatible chat-completions (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`) |
| Responsibility | grounded explanation of the verified Route Profile |
| Failure | `LLM_FAILURE` → deterministic fallback text; analysis remains available |
| Input | structured Route Profile only — never free-form client data (`TRD` §46–§47) |

Rules:
- LLM never calculates risk, never adds facts, never claims safety guarantees.
- If key absent or call fails, produce a fallback sentence from the structured profile (`MASTER_RULES` §16).

---

## Provider Abstraction Layer

```
RoutingProvider   -> geocode(), route(), normalize()      (TRD §94)
FacilityProvider  -> search(), normalize(), health_check() (TRD §93)
LLMService        -> generate_explanation(), validate_output(), handle_error() (TRD §95)
```

Provider-specific SDKs live only inside these modules.

## Validation & Freshness

- External responses validated against typed schemas before use (`TRD` §116).
- Track data timestamps; never imply live conditions from stale imagery (`TRD` §135).
- Respect provider rate limits; handle 429 with backoff; cache results (`TRD` §96–§98).

## Related Docs

- `04_DATA_MODEL.md` (tables fed by these sources)
- `06_SCRAPING_SPEC.md` (permitted collection policy)
- `02_TRD.md` §45–§48, §93–§98