# 13_TESTING.md — SafeRoute AI Testing Specification

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Authoritative Testing Specification
**Version:** 1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_RULES.md` > `01_PRD.md` > `02_TRD.md` > `03_ARCHITECTURE.md` > this document
**Companion:** `09_ERROR_HANDLING.md` (error-path tests), `07_API_CONTRACT.md` (contract tests), `08_UI_SPEC.md` (frontend states/a11y), `10_SECURITY.md` / `security_handling.md` (security tests), `12_GITHUB_ACTIONS.md` (CI)

Any unresolved testing decision is marked `[DECISION REQUIRED]`.

---

## 1. PURPOSE

This document defines how SafeRoute AI is tested. It makes the test strategy, layers, required coverage, fixture policy, security/error-path coverage, and the verification commands concrete and checkable.

The goals are:

- Prove that important business logic behaves correctly (routing, aggregation, risk, facilities, LLM grounding, API).
- Prove that failures are handled per `09_ERROR_HANDLING.md` without fabrication.
- Keep the suite **fast, deterministic, and offline**.
- Ensure every change can be verified with a documented command (backend: `pytest -q`, `ruff check .`, `mypy app`; frontend: `npm test`, `npm run lint`).

This document mirrors `02_TRD.md` §107–§115 and `MASTER_PROJECT_PROMPT.md` §67–§69.

---

## 2. TEST STRATEGY

### 2.1 Principles

1. **Fast unit tests first.** Pure logic (normalization, aggregation, risk math, validation, mapping) is unit-tested with no I/O.
2. **Focused integration tests, not a sprawling E2E suite.** Integration tests cover the boundaries that matter: FastAPI endpoints ↔ services, and services ↔ mocked providers/database.
3. **External providers are always mocked.** Routing, facility, and LLM providers are mocked in automated tests (`02_TRD.md` §115).
4. **Never depend on the live network.** A test that needs the internet is not a test that belongs in the suite. Live smoke checks are manual and documented (`03_ARCHITECTURE.md` §12).
5. **No fabricated data in tests.** Fixtures are labeled `MOCK` and live only in test fixtures. No test may ship mock values as production behavior.
6. **Provider responses are schema-validated in tests.** Malformed responses are part of the fixture set.
7. **Determinism.** No time-of-day, RNG, or network-dependent assertions. Risk-engine tests assert exact expected scores.
8. **Zero ≠ unavailable is enforced in tests** (`MASTER_PROJECT_PROMPT.md` §26, `09_ERROR_HANDLING.md` §10.7).

### 2.2 What is not covered by automated tests

- Real YOLO accuracy on real roads (ML evaluation is separate; `01_PRD.md` §28, `02_TRD.md` §154).
- Live provider behavior and SLAs.
- Real-world GPS/imagery timeliness.
- Manual map visual checks (covered by frontend component tests + manual QA).

---

## 3. TEST LAYERS

```
Unit Tests
    ↓
Integration Tests
    ↓
API / Contract Tests
    ↓
ML Pipeline Tests
    ↓
End-to-End Tests
```

(`02_TRD.md` §107)

Every layer is always runnable offline with mocked providers and a test database (SQLAlchemy + Alembic migrations applied to a throwaway PostgreSQL 16 test schema, or an in-memory equivalent where the stack supports it).

---

## 4. BACKEND TEST COMMANDS

Run from `backend/`:

```bash
pytest -q          # full backend suite
pytest tests/unit  # unit tests only
pytest tests/api   # API/contract tests only
ruff check .       # lint (must pass)
mypy app           # type checking (must pass)
```

(`03_ARCHITECTURE.md` §12)

Frontend, run from `frontend/`:

```bash
npm test           # Vitest + React Testing Library (watch by default; CI: npm test -- --run)
npm run lint       # eslint
npm run build      # type-check + production build
```

CI runs: install → lint → unit tests → integration tests → build → security checks → deploy (`02_TRD.md` §126, `12_GITHUB_ACTIONS.md`).

---

## 5. UNIT TESTS — TRD §108 MAPPING

Unit tests MUST cover the seven required areas of `02_TRD.md` §108.

### 5.1 Route normalization

- Provider response (OSRM shape) → internal `Route` model: `route_id`, `request_id`, `distance_meters`, `duration_seconds`, `geometry`, `coordinates`, `segments`, `provider`, `provider_route_id`.
- Coordinate list extraction and geometry decode failures raise mapped errors.
- Unknown/extra provider fields are ignored, never leaked.
- 1, 2, 3, and 4 routes are supported; never padded to 4 (`03_ARCHITECTURE.md` §5).

### 5.2 Coordinate validation

- Latitude out of `[-90, 90]` → invalid.
- Longitude out of `[-180, 180]` → invalid.
- Missing/non-numeric/`NaN` coordinates → invalid.
- Null vs missing vs zero-coordinate handling (0,0 is a valid coordinate; absence is `unavailable`).
- Equal source and destination (identical coords) → defined behavior per contract.
- Error codes map to `07_API_CONTRACT.md` §9 (`INVALID_COORDINATES`).

### 5.3 Hazard aggregation

- Image-level `HazardDetection` → route-level unique hazards with duplicate suppression.
- Same pothole in 5 overlapping images → counted once (`MASTER_RULES.md` §12).
- Segment association, geographic clustering, and type preservation.
- Empty detection set → zero hazards (distinct from analysis not run).
- Model version traceability preserved on aggregated hazards (`04_DATA_MODEL.md` §7.9/§7.11, §7.13).

### 5.4 Risk calculation

- Exact-score assertions with known inputs/configurations (deterministic, `02_TRD.md` §33).
- Normalization to 0–100, boundary and extreme values.
- Missing optional inputs → `risk_status=unavailable`, **never `score=0`** (`09_ERROR_HANDLING.md` §10.6).
- Weight configuration parsing (`HAZARD_WEIGHTS`) and invalid/config errors fail fast.
- Cross-check `04_DATA_MODEL.md` §7.15/§7.16 traceability chain.

### 5.5 Facility aggregation

- Facility results grouped by category with `count` and `nearest_distance_km` (`02_TRD.md` §41).
- Distance-from-route calculation (nearest route point; straight-line ≠ driving distance, `02_TRD.md` §40).
- Dedup by provider ID / coordinates / name similarity.
- Zero results (provider succeeded) vs provider failure (`status=unavailable`) are distinct outputs.

### 5.6 LLM input preparation

- LLM receives **only** verified structured profile fields (`03_ARCHITECTURE.md` §6.11): `route_id`, `distance_km`, `duration_minutes`, `risk_score`, hazards, facilities.
- Missing fields are rendered as `unavailable`, never fabricated or defaulted to zero.
- The system instruction/prompt version is stable and testable.
- Unsupported client-supplied numerical values are never accepted as authoritative input (`02_TRD.md` §56).

### 5.7 Error mapping

- Domain/service exceptions → error codes in the catalogue (`09_ERROR_HANDLING.md` §8): `VALIDATION_ERROR`, `INVALID_COORDINATES`, `ROUTING_PROVIDER_ERROR`, `NO_ROUTE_FOUND`, `IMAGE_UNAVAILABLE`, `YOLO_INFERENCE_FAILED`, `RISK_CALCULATION_FAILED`, `FACILITY_PROVIDER_ERROR`, `LLM_PROVIDER_ERROR`, `RATE_LIMITED`, `INTERNAL_ERROR`.
- No stack traces, secrets, or internal URLs in user-facing output.

---

## 6. RISK ENGINE TESTS — TRD §110

Cover every case in `02_TRD.md` §110:

- **No hazards** → score reflects empty set within normalization (documented baseline; never negative).
- **One hazard** → exact expected score for a single configured weight.
- **Multiple hazards** → summation over `weight × severity × confidence × exposure`.
- **Low confidence** (below threshold contributions) and **high confidence** → confidence term scales score as designed.
- **Different hazard types** → per-type weights applied (e.g., pothole vs debris).
- **Maximum values** → score saturates/overflows correctly at normalization bounds.
- **Missing optional values** (missing severity/exposure) → handled by documented defaults or `unavailable`, never a crash or fabricated value.
- **Determinism** → same input + same config + same model output ⇒ same score, asserted twice in the same run.
- **Version invariance** → changing weights bumps `risk_engine_version`; historical assertions remain pinned to the config version.

Any test that documents exact expected scores must reference the formula in the risk-engine documentation so the test and spec cannot drift silently.

---

## 7. FACILITY TESTS — TRD §111

Cover every case in `02_TRD.md` §111:

- **No facilities** → `count: 0` per category (provider succeeded, empty corridor).
- **One facility** → correctly categorized, counted, nearest distance computed.
- **Multiple facilities** → per category counts + nearest per category.
- **Duplicate facilities** → deduplicated (provider ID preferred, then coordinates/name).
- **Different categories** → each category aggregated independently; no cross-category mixing.
- **Provider failure** → `{ "status": "unavailable", "reason": ... }`, never zero (`02_TRD.md` §42).
- **Missing coordinates** → facility without coords is either excluded with a recorded reason or handled as unavailable; never assigned a guessed location.

Corridor semantics are tested: only facilities within `FACILITY_SEARCH_RADIUS_KM` of the route are returned (`MASTER_PROJECT_PROMPT.md` §23).

---

## 8. API / CONTRACT TESTS — TRD §112

Cover every case in `02_TRD.md` §112 against the contract in `07_API_CONTRACT.md`:

- **Valid request** → `POST /api/v1/route-requests` returns normalized routes (`07_API_CONTRACT.md` §7.1).
- **Invalid request** (malformed JSON, wrong types) → 400/422.
- **Missing fields** (source/destination absent) → validation error, no partial write.
- **Invalid coordinates** → `422 INVALID_COORDINATES`.
- **No route** → `404 NO_ROUTE_FOUND`, error envelope (`07_API_CONTRACT.md` §9.4).
- **Provider failure** → `502 ROUTING_PROVIDER_ERROR`; remaining-valid-routes behavior per `09_ERROR_HANDLING.md` §10.1.
- **Timeout** → external call exceeds `REQUEST_TIMEOUT` → `504 ANALYSIS_TIMEOUT` or async-job continuation (`GET /api/v1/jobs/{job_id}`, §7.7).
- **Rate limit** → `429 RATE_LIMITED` + `Retry-After` (`07_API_CONTRACT.md` §11.8).

Contract assertions include: endpoint existence, method, request schema, response schema, error envelope shape, and HTTP status codes for every endpoint in `07_API_CONTRACT.md` §7.1–§7.17 (route, routes-list, segments, images, hazards, detections, risk, facilities, facilities/summary, analysis, llm/explanations, health).

---

## 9. ML PIPELINE TESTS — TRD §109

Cover every case in `02_TRD.md` §109:

- **Model loading** → yololoader resolves `MODEL_PATH`; missing/corrupt artifact → `MODEL_LOAD_FAILED`, `YOLO status = unavailable` (`09_ERROR_HANDLING.md` §10.4, `04_DATA_MODEL.md` §7.13).
- **Input preprocessing (OpenCV)** → read, validate, resize, color conversion, normalize; invalid dimensions/encoding → rejected with reason (`04_DATA_MODEL.md` §7.8).
- **Detection parsing** → raw YOLO output → structured `HazardDetection` with class, confidence, bbox, image/route/segment ids, model version.
- **Class mapping** → classes derive from `ml/dataset/data.yaml`; unknown class → rejected/flagged, never silently passed.
- **Confidence filtering** → detections below `YOLO_CONFIDENCE_THRESHOLD` dropped; threshold configurable.
- **Empty detection results** → valid empty list (not an error).
- **Invalid images** → corrupted, wrong MIME, oversized → `processing_status=invalid`, segment marked not-analyzed (never "no hazards", `09_ERROR_HANDLING.md` §10.2).
- **Model failure** → per-image bounded retry, then safety unavailable; route + facilities preserved; no fabricated detections.

Model-version provenance is asserted: every detection row carries `model_version` (`04_DATA_MODEL.md` §7.9).

---

## 10. ERROR-PATH TESTS — 09_ERROR_HANDLING §15

The following error-path tests are REQUIRED (mirrors `09_ERROR_HANDLING.md` §15 and `MASTER_PROJECT_PROMPT.md` §68):

### 10.1 Isolation + no fabrication

- Routing provider fails, facility succeeds → result contains route + facilities, safety partial; nothing invented.
- YOLO fails → `safety.status=unavailable`; facility and route still returned (`09_ERROR_HANDLING.md` §10.4).
- LLM fails → deterministic fallback sentence (`fallback: true`), structured analysis intact (`§10.8`).
- Database failure → explicit `DATABASE_ERROR`; no phantom rows/results (`§10.9`).

### 10.2 Zero vs unavailable (mandatory)

- Provider successful search returning zero → `count: 0`.
- Provider failure → `{ "status": "unavailable" }`.
- Test asserts the two are NEVER conflated (`MASTER_PROJECT_PROMPT.md` §26, `08_UI_SPEC.md` §14.6).

### 10.3 Partial envelopes

- One subsystem fails → assert partial envelope shape (`07_API_CONTRACT.md` §9.4) and the corresponding frontend states are represented in API output (`09_ERROR_HANDLING.md` §13).
- Assert exit statuses are one of `succeeded | partial | failed | unavailable | cancelled | timed_out` (`§12.3`).

### 10.4 Retry policy

- Transient (5xx/timeout) → bounded retries with backoff (`09_ERROR_HANDLING.md` §11.1).
- Idempotency: retries never create duplicates (honor `Idempotency-Key`, `07_API_CONTRACT.md` §11.7).
- 4xx/invalid input/security violations → never retried.

---

## 11. END-TO-END TESTS — TRD §113

Minimum complete flow (`02_TRD.md` §113):

```
Enter Source → Enter Destination → Generate Routes → Select Route
→ Run Analysis → Process Images → YOLO Detection → Hazard Aggregation
→ Risk Calculation → Facility Search → Route Profile
→ LLM Explanation → Display Result
```

E2E tests run against a real FastAPI app + real test database + mocked providers. Frontend E2E (if introduced) drives the UI via the browser against the same stubbed backend.

Scenarios:

- Full happy path: source → dest → routes → analysis → hazards → facilities → explanation rendered.
- Partial path: facilities fail → full analysis minus facilities still displayed with `unavailable` chip.
- LLM failure: structured dashboard renders; explanation area shows fallback/unavailable text.
- Route has no imagery → "Road imagery unavailable for this section." is shown, never "No hazards detected." (`MASTER_PROJECT_PROMPT.md` §11).

---

## 12. SECURITY TESTS — MASTER_PROJECT_PROMPT §69

Cover the list in `MASTER_PROJECT_PROMPT.md` §69 and `security_handling.md` §21:

- **XSS** → malicious facility names/routes/LLM text render safely in React (no raw `dangerouslySetInnerHTML` of untrusted text; sanitized).
- **SQL injection** → parameterized queries; SQLi attempts on route id/filters return validation errors, never execute.
- **CSRF** → where applicable; state-changing endpoints protected per `MASTER_PROJECT_PROMPT.md` §44.
- **Auth bypass / authorization bypass** → every protected endpoint denies without valid credentials (when auth is enabled).
- **Upload abuse** → wrong MIME, fake extension, oversized, corrupt image → rejected (`02_TRD.md` §76, `09_ERROR_HANDLING.md` §10.12).
- **Prompt injection** → untrusted text (facility/route/user content) in a prompt cannot redefine system instructions (`MASTER_PROJECT_PROMPT.md` §47).
- **Malicious LLM output** → output validated; unsupported numerical claims flagged → fallback (`02_TRD.md` §48).
- **Rate-limit bypass** → rapid requests receive `429`; `X-Forwarded-For` spoofing does not bypass limits (`07_API_CONTRACT.md` §11.8).
- **Secret exposure** → bundle scans, log assertions: no API keys, tokens, DB credentials in responses/logs; `.env` never committed; CI secret scan (`security_handling.md` §21, `runbooks/credential-reevocation-or-leak.md`).
- **API abuse** → oversized payloads, malformed bodies, unexpected query params → rejected safely.

---

## 13. TEST DATA & FIXTURES — TRD §114

Maintain fixtures for (`02_TRD.md` §114):

- **Routes** — OSRM-shaped and normalized (1–4 routes, plus provider failures).
- **Images** — valid/invalid/corrupt/oversized samples (small binary fixtures, generated at test time where possible).
- **YOLO outputs** — detection lists with all classes, empty lists, unknown classes, low/high confidence.
- **Hazards** — raw detections and aggregated results, overlapping-image duplication cases.
- **Facilities** — per-category results, duplicates, zero results, provider-error responses.
- **Risk** — input tuples + expected exact scores (labeled OUTPUT for the documented formula).
- **LLM structured input** — canonical profiles including `unavailable` fields.

### 13.1 Fixture policy

- All fixture files live under `backend/tests/fixtures/` (and `frontend/src/**/__fixtures__/` where needed).
- Every fixture is clearly labeled `MOCK` / `TEST` (not silently production).
- No fixture contains real secrets.
- No test hits the live network; mock adapters are returned for `ROUTING_PROVIDER`, `FACILITY_PROVIDER`, `LLM_API_KEY` per `02_TRD.md` §115.
- Example values in fixtures are illustrative and MUST NOT be interpreted as real system output (`02_TRD.md` §151).

---

## 14. FRONTEND TESTS

Framework: Vitest + React Testing Library. Run with `npm test`; CI uses `--run`.

### 14.1 State rendering tests (`08_UI_SPEC.md` §14)

- **Loading** → skeleton/spinner shown; no fake progress percentages (`MASTER_PROJECT_PROMPT.md` §51).
- **Error** → readable error message + Retry action; never `risk: 0` on failure (`08_UI_SPEC.md` §14.5, §14.9).
- **Empty** → accurate empty copy (e.g., "No facilities found within the route corridor.").
- **Partial** → status chips per domain (Route ✓, Safety ✗, Facilities ✓, AI —) reflect partial envelope (`08_UI_SPEC.md` §14.8).
- **Unavailable** → visually and textually distinct from zero; "Facility information is currently unavailable." ≠ "0 found" (`08_UI_SPEC.md` §14.6).

### 14.2 Accessibility (`08_UI_SPEC.md` §16, `MASTER_PROJECT_PROMPT.md` §74)

- Keyboard navigation across search, route cards, map controls, filters.
- Semantic HTML; visible focus; accessible labels; ARIA where needed.
- Route/hazard/facility information readable by screen readers.
- Contrast and non-color-only information (routes never depend on color alone).

### 14.3 Other frontend tests

- Typed client: request/response shapes mirror backend schemas; error envelope parsed into typed state.
- Marker/icon config per facility category and hazard type.
- Route-card render with numeric formatting and `unavailable` placeholders.
- Search form validation (client-side) aligns with backend rules.

---

## 15. CI INTEGRATION

Per `02_TRD.md` §126 and `12_GITHUB_ACTIONS.md`:

```text
Install dependencies → Lint → Unit tests → Integration tests → Build
→ Security checks → Deploy (≈ no deploy if critical tests fail)
```

- Backend job: `ruff check .` → `mypy app` → `pytest -q` (offline).
- Frontend job: `npm run lint` → `npm test -- --run` → `npm run build`.
- Migrations run against a PostgreSQL 16 test instance; failure handles per `runbooks/database-migration-failure.md`.
- Secret scan and dependency CVE scan on every push.
- Branching per `02_TRD.md` §128 (`main` / `develop` / `feature/*` / `fix/*`); commits per §127.

---

## 16. DEFINITION OF DONE (TESTS)

A feature's testing is complete only when:

```
[ ] Important logic has unit tests (TRD §108 mappings)
[ ] Error paths tested per 09_ERROR_HANDLING §15
[ ] Redundant UI states tested (loading/error/empty/partial/unavailable)
[ ] Tests run offline with mocked providers
[ ] ruff check . and mypy app pass (backend)
[ ] npm run lint and npm test pass (frontend)
[ ] No fabricated data in fixtures/assertions
[ ] Changelog/microtask updated where required (15_MICROTASKS.md, 16_CHANGELOG.md)
```

Cross-check with `03_ARCHITECTURE.md` §13 Definition of Done before declaring a feature complete.

---

## 17. RELATED DOCUMENTS

- `02_TRD.md` §107–§115 (layers, unit/ML/risk/facility/API/E2E, fixtures, mocking), §126–§128 (CI, git)
- `03_ARCHITECTURE.md` §12 (verification commands), §13 (definition of done)
- `09_ERROR_HANDLING.md` §15 (error-path tests), §11 (retry/fallback)
- `07_API_CONTRACT.md` §9 (errors), §11.3 (null vs absent vs zero vs unavailable), §11.7–§11.8 (idempotency, rate limiting)
- `08_UI_SPEC.md` §14 (states), §16 (accessibility), §21 (UI testing)
- `10_SECURITY.md` / `security_handling.md` §21 (security tests)
- `MASTER_PROJECT_PROMPT.md` §67–§69 (testing/failure/security testing), §26 (zero vs unavailable)
- `runbooks/` (incident procedures)

---

# END OF TESTING SPECIFICATION