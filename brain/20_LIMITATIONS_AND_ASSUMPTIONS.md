# 20_LIMITATIONS_AND_ASSUMPTIONS.md — SafeRoute AI Limitations & Assumptions

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Authoritative Limitations & Assumptions Specification
**Version:** 1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_RULES.md` > `01_PRD.md` > `02_TRD.md` > `MASTER_PROJECT_PROMPT.md` §92–§95 > this document
**Companion:** `05_DATA_SOURCES.md`, `06_AI_SOURCES.md`, `16_MONITORING.md` (auditability), `15_DEPLOYMENT.md`

This document is the authoritative record of what SafeRoute AI can and cannot claim, the assumptions the system is built on, and the licensing/provider decisions that are still open. Unresolved decisions are marked `[DECISION REQUIRED]`.

---

## 1. PURPOSE

SafeRoute AI is a decision-support navigation system, not a safety guarantee system (`MASTER_PROJECT_PROMPT.md` §4). Every component — imagery, detection model, risk score, facility data, LLM — has defined limits. This document makes those limits explicit so that:

- product copy never overclaims,
- the frontend communicates uncertainty honestly (`02_TRD.md` §136–§138),
- the LLM stays grounded and never fills gaps with guesses (`MASTER_RULES.md` §16),
- and documentation references a single, authoritative limitations record.

---

## 2. IMAGERY LIMITATIONS

### 2.1 Imagery may be incomplete or old (temporal limitation)

- SafeRoute AI never assumes imagery exists for every road (`MASTER_PROJECT_PROMPT.md` §11). States are: available / partially available / unavailable / collection failed.
- Road images may be **old** and do not represent **current** road conditions (`MASTER_PROJECT_PROMPT.md` §57, `02_TRD.md` §135–§136). A pothole in a 6-month-old image may be fixed; a new pothole may be invisible to older imagery.
- The system preserves `timestamp`, `source`, and collection date when available and must **not present imagery as real-time road condition** (`02_TRD.md` §135).
- Dedicated real-time imagery is out of scope; the system is inherently limited by its data sources.
- **Assumption:** imagery providers and their coverage terms permit the intended use — this is a `[DECISION REQUIRED]` item (see §9).

### 2.2 Detection confidence vs actual danger

- YOLO confidence measures *detection confidence* (how sure the model is of an object in an image). It is **not** the probability of real-world road danger (`MASTER_PROJECT_PROMPT.md` §15).
- The UI must not imply `91% confidence = 91% danger`. Hazard risk is computed separately and deterministically by the Risk Engine.

---

## 3. YOLO / MODEL LIMITATIONS

### 3.1 False positives and false negatives

- The detection model produces **false positives** (objects marked that are not the hazard) and **false negatives** (real hazards missed). No object detector is perfect (`MASTER_PROJECT_PROMPT.md` §92).
- Low-confidence detections are filtered by the configured threshold; below-threshold hazards are simply not reported.
- The system **never claims zero hazards** because a model found none: absence of detections in available imagery ≠ absence of hazards on the road. "Road imagery unavailable for this section" is the correct message when imagery is missing (`MASTER_PROJECT_PROMPT.md` §11).
- **Assumption:** the model is trained only on classes present in the project dataset (pothole, road_crack, damaged_road, obstacle, debris as applicable); classes outside `data.yaml` are not detected (`MASTER_RULES.md` §8). Detection quality is validated with documented ML metrics, never asserted from training completion alone (`02_TRD.md` §54).

### 3.2 Detection confidence ≠ danger

- Already covered in §2.2; repeated here because it is a standing assumption for all downstream risk interpretation. The Risk Engine combines weight × severity × confidence × exposure into a project-defined score — it is not a probabilistic hazard forecast (`02_TRD.md` §30–§34).

---

## 4. FACILITY LIMITATIONS

- Facility data comes from external providers (default Overpass/OpenStreetMap) and is limited by **provider coverage, completeness, and freshness** (`02_TRD.md` §137).
- A provider that returns no results after a successful search is a **true zero**. A provider that fails is `unavailable`. These are never blurred (`MASTER_PROJECT_PROMPT.md` §26).
- The system never invents phone numbers, addresses, opening hours, ratings, or availability; it displays only fields the provider actually returned (`MASTER_PROJECT_PROMPT.md` §24).
- "Nearby" means within the configured route corridor (`FACILITY_SEARCH_RADIUS_KM`). Facilities outside the corridor are not considered, even if they are "nearby" in an unconfigured sense (`02_TRD.md` §38).
- **Distance semantics:** facility distance is a route-relative geometric/straight-line distance, not a driving distance. It is never presented as driving distance (`02_TRD.md` §40).

---

## 5. ROUTING / GEOGRAPHIC LIMITATIONS

### 5.1 Provider may return fewer than 4 routes

- The system requests up to `MAX_CANDIDATE_ROUTES`=4, but the number of routes shown is whatever the routing provider actually returns — 1, 2, 3, or 4 (`MASTER_RULES.md` §6). No route is fabricated to reach four (`03_ARCHITECTURE.md` §5).
- If no route exists, the system returns a clear no-route error; it does not invent one (`09_ERROR_HANDLING.md` §10.1).

### 5.2 Straight-line vs driving distance

- Route distances/durations come from the routing provider. Facility distances are straight-line from the route (**≠ driving distance**, §4). Any coordinate comparison uses appropriate geodesic calculations and is described accurately (`02_TRD.md` §40).

### 5.3 Weather / traffic change conditions

- SafeRoute AI does not model weather or live traffic. Road conditions inferred from imagery may be invalidated by weather (potholes hidden by water, debris moved by storms) and road works. The score reflects the analyzed imagery and configured data, not the moment of travel (`MASTER_PROJECT_PROMPT.md` §92, §115).

---

## 6. RISK SCORE LIMITATION

- The risk score is **project-defined**, deterministic, and versioned — it is **not an official government or universal road-safety standard** (`MASTER_RULES.md` §13, `MASTER_PROJECT_PROMPT.md` §19).
- A low score means *low risk per the implemented analytical model and available data*; it never means *completely safe* (`02_TRD.md` §138).
- If inputs are missing, `risk_status = unavailable` — never `score = 0` (`09_ERROR_HANDLING.md` §10.6).
- **Assumption:** risk weights, severities, and normalization are documented in `10_RISK_ENGINE.md`; any change increments `risk_engine_version` (`MASTER_PROJECT_PROMPT.md` §112).

---

## 7. LLM LIMITATION

- The LLM explains **only verified structured data** supplied by the backend. It is an explanation layer, never a decision engine (`MASTER_RULES.md` §16).
- If data is absent, the LLM says it is unavailable. The LLM never invents hazards, facilities, routes, distances, scores, or statistics, and never guarantees safety (`MASTER_PROJECT_PROMPT.md` §35–§37).
- LLM output is generated text and is validated; the structured data remains authoritative (`08_UI_SPEC.md`, `MASTER_PROJECT_PROMPT.md` §77).
- On provider failure/timeout the system returns a **deterministic fallback** sentence; the structured analysis is never destroyed by LLM failure (`09_ERROR_HANDLING.md` §10.8).

---

## 8. LOCATION & PRIVACY ASSUMPTIONS

- **Location accuracy depends on the provider/GPS.** Hazard and facility coordinates inherit provider precision; the system does not imply centimeter-level accuracy (`MASTER_PROJECT_PROMPT.md` §58).
- **No PII collection.** The system processes source/destination coordinates, route data, imagery, and usage data only as required; it does not collect personal identifiers, does not retain exact locations unnecessarily, and never transmits location data to unrelated services (`MASTER_PROJECT_PROMPT.md` §87–§88).
- Exact coordinates are not logged beyond operational need (`09_ERROR_HANDLING.md` §12.1).

---

## 9. LICENSING / PROVIDER DECISIONS

These must be resolved before production deployment (`MASTER_PROJECT_PROMPT.md` §89–§91).

### 9.1 Road imagery provider — `[DECISION REQUIRED]`
- **What is missing:** the finalized road imagery source.
- **Why it matters:** `MASTER_PROJECT_PROMPT.md` §90 requires verifying the source permits the intended use (license, API restrictions, storage/display rules, commercial usage).
- **Options:** approved street-level imagery provider; project-owned imagery; authorized datasets; future user-contributed imagery (`MASTER_PROJECT_PROMPT.md` §10).
- **Recommended consideration:** pick a provider whose license allows the intended display and caching behavior; record license + attribution in `05_DATA_SOURCES.md`. Until decided, this document and `05_DATA_SOURCES.md` carry `[DECISION REQUIRED]`.

### 9.2 YOLO11 / model & dataset licenses — `[DECISION REQUIRED]`
- **What is missing:** final license verification for the model artifact and its training dataset.
- **Why it matters:** `MASTER_PROJECT_PROMPT.md` §91 requires recording model source, license, dataset source/license, and commercial-use restrictions before commercial deployment.
- **Recommended consideration:** use the default YOLO11 (AGPL-3.0) only where compatible, or select an alternatively-licensed export/workflow; document dataset provenance and annotation rights in `06_AI_SOURCES.md`. Until decided, keep the artifact out of any committed distribution.

---

## 10. DATA FRESHNESS & OFFLINE BEHAVIOR

- **Offline/cached data is labeled.** Previously cached data may be shown when connectivity fails, but never as live (`MASTER_PROJECT_PROMPT.md` §61). Cache entries carry version/configuration keys to prevent stale-model results from being reused (`02_TRD.md` §85–§86).
- Old imagery is presented as historical, with timestamp surfaced where available (§2.1).

---

## 11. USER REMAINS FINAL DECISION-MAKER

- SafeRoute AI presents evidence; the user decides the trade-off (distance, duration, risk, facilities) that matters to them (`MASTER_PROJECT_PROMPT.md` §29, §59).
- The system does not declare a universal "best" route and never implies an AI guarantee.
- **Assumption:** frontend stays transparent — structured data, version tags, and per-domain statuses are visible, and no opaque merged score is fabricated (`MASTER_RULES.md` §14, `03_ARCHITECTURE.md` §6.9).

---

## 12. RECOMMENDED USER-FACING SAFETY DISCLAIMER

Recommended wording for the product (from `MASTER_PROJECT_PROMPT.md` §93), placed where users can see it without destroying usability (e.g., footer, first-analysis banner, about/help):

> SafeRoute AI provides road-condition and route-related information based on available data and analyzed imagery. Results may be incomplete, outdated, or affected by model and data limitations. Users remain responsible for following traffic laws and exercising appropriate judgment.

Rules for placement and phrasing:
- Use this text (or its direct, faithful equivalent) as the canonical disclaimer.
- Make it visible once per session near the analysis UI / footer; do not make it so prominent it destroys usability, but do not hide it.
- Do not combine it with guarantee language ("safest route", "100% safe", "accident proof") — those phrases are forbidden (`MASTER_PROJECT_PROMPT.md` §21).
- The AI explanation section and route cards may reference the same limitation inline where a user could misinterpret a low score as safety (`02_TRD.md` §136): e.g., "Road-condition analysis is based on available imagery and may not reflect current conditions."

---

## 13. SUMMARY OF HARD ASSUMPTIONS

1. Imagery exists for only part of the network, may be old, and is never real-time.
2. Detection confidence ≠ danger probability; risk is computed deterministically.
3. Facility/coverage = provider-limitted; zero ≠ unavailable.
4. Routes = 1–4 as returned; nothing is fabricated; distances are route-authored, facility distances are straight-line.
5. Weather/traffic are not modeled; conditions change over time.
6. Risk score is project-defined and versioned, not an official standard.
7. LLM is grounded in available verified data only and cannot fill gaps.
8. Location accuracy inherits provider/GPS precision.
9. No PII collection; coordinates minimized in logs.
10. Imagery provider license verified (`[DECISION REQUIRED]`).
11. Model/dataset licenses verified (`[DECISION REQUIRED]`).
12. Offline/cached data is always labeled as cached/stale.
13. The user is the final decision-maker.

---

## 14. RELATED DOCUMENTS

- `MASTER_PROJECT_PROMPT.md` §92–§95 (limitations, disclaimer, no-fabrication)
- `02_TRD.md` §135–§138 (data freshness, imagery/facility/risk limitations), §86 (cache invalidation)
- `09_ERROR_HANDLING.md` §4, §10 (unavailable ≠ zero, no fabrication)
- `05_DATA_SOURCES.md`, `06_AI_SOURCES.md` (provider/license records)
- `16_MONITORING.md` §7 (auditability/reproducibility)
- `08_UI_SPEC.md` §13 (AI disclaimers in UI)

---

# END OF LIMITATIONS & ASSUMPTIONS SPECIFICATION