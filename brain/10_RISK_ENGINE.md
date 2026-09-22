# 10_RISK_ENGINE.md — SafeRoute AI Risk Engine Specification

*(may also be referenced as `docs/RISK_ENGINE.md`)*

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Risk Engine Specification (authoritative formula, calibration, determinism, testing)
**Version:** v1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_RULES.md` > `01_PRD.md` > `02_TRD.md` > `03_ARCHITECTURE.md` > `04_DATA_MODEL.md` > `07_API_CONTRACT.md` > this document
**Companion:** `07_API_CONTRACT.md` §7.12 (wire format), `04_DATA_MODEL.md` §7.15–§7.16 (persistence), `09_ERROR_HANDLING.md` §10.6 (failure), `13_TESTING.md` (test plan)

> This document is the exact mathematical implementation referenced by `02_TRD.md` §32 and `02_TRD.md` §155. If this document conflicts with a code comment, the code comment must be corrected to match — never the reverse.

---

## 1. POSITION OF THE RISK ENGINE

The Risk Engine is an **independent, deterministic, server-side calculation stage** in the SafeRoute AI pipeline:

```
HAZARD AGGREGATION → RISK ENGINE → (risk_score, risk_components) → ROUTE PROFILE → LLM (explanation only)
```

It is:

- **Deterministic** — same input + same configuration + same model output always produces the same score (`MASTER_RULES.md` §13, `02_TRD.md` §33, `04_DATA_MODEL.md` §7.16).
- **Never computed by the LLM** — the LLM is prohibited from calculating, altering, or reinterpreting the score (`02_TRD.md` §19, §47, §139). The LLM may only *restate* a score already produced here.
- **A project-defined analytical metric** ranging **0–100**. It is **NOT** an official government rating, a universal road-safety standard, or a safety guarantee (`MASTER_RULES.md` §13; `07_API_CONTRACT.md` §7.12). It represents "the implemented analytical model applied to available imagery."
- **Never merged with facilities** — hospitals, medical stores, restaurants, hotels, petrol pumps, and police stations are separate dimensions (`MASTER_RULES.md` §14, `03_ARCHITECTURE.md` §6.9). They contribute **zero** to this formula.

---

## 2. NON-NEGOTIABLE INVARIANTS

| # | Invariant | Source |
|---|-----------|--------|
| I1 | The Risk Engine is the **only** producer of the authoritative `risk_score`. | `04_DATA_MODEL.md` §7.15 |
| I2 | Same inputs + config + model output ⇒ byte-identical score. | `02_TRD.md` §33 |
| I3 | `risk_score` never equals `0` merely because something failed. Failure ⇒ `status="unavailable"`, `risk_score=NULL`. | `07_API_CONTRACT.md` §7.12; `09_ERROR_HANDLING.md` §10.6 |
| I4 | `risk_status` is always one of `calculated` or `unavailable` — never `"0"`, never `""`. | `04_DATA_MODEL.md` §7.15 |
| I5 | The LLM never receives authority to change the score. | `02_TRD.md` §47 |
| I6 | Every row stores `algorithm_version` + `configuration_version` so history is reproducible. | `04_DATA_MODEL.md` §7.15–§7.16 |

---

## 3. INPUTS AND PRE-CONDITIONS

The engine consumes the **aggregated, unique physical hazards** (never raw YOLO detections — `04_DATA_MODEL.md` §7.10):

| Input | Source | Notes |
|-------|--------|-------|
| `hazards`: list of unique hazards | Hazard Aggregation (`04_DATA_MODEL.md` §7.11) | each has `hazard_type`, `confidence_summary`, `segment_id`, status |
| `segments`: authoritative segment geometry | Route Normalization (`02_TRD.md` §13) | each has `segment_id`, `sequence`, `geometry`, `length_m` |
| `route_length_m` | Route Normalization | = Σ segment lengths (authoritative routing output) |
| `images_analyzed`, `segments_analyzed` | Image/YOLO pipeline | coverage bookkeeping for status decisions |
| `model_version` | `04_DATA_MODEL.md` §7.13 | YOLO version used for detections |
| `config` | resolved risk configuration (§15) | weights, severities, gain, modes, thresholds |

**Pre-condition:** Hazards carry `hazard_type` drawn from the active model class list only (`02_TRD.md` §23). A hazard with a class absent from the active model/dataset is a **configuration error** (fail fast at startup) — the engine never guesses a weight for an unknown class.

---

## 4. RISK FORMULA (EXACT)

```
risk = Σ_i ( pothole_weight × ... )      # conceptual model (MASTER_RULES.md §13, 02_TRD.md §32)
```

Implemented exactly:

```
raw = Σ over unique hazards h in hazards:
        weight( class(h) )
      × severity( class(h) )
      × confidence(h)
      × exposure( segment(h) )
```

### 4.1 Variable definitions

| Variable | Definition | Domain |
|----------|-----------|--------|
| `weight(class)` | Configurable per-class weight. Captures severity-of-consequence *rank* of the class (deep potholes are more consequential than scattered debris). | `> 0`, default table §4.2 |
| `severity(class)` | Configurable per-class physical-severity factor. | `(0, 1]`, default table §4.3 |
| `confidence(h)` | `confidence_summary` of the aggregated hazard (default: **max** of member detections; configurable to `mean` — §15). | `[0, 1]` |
| `exposure(segment)` | Share of the route occupied by the hazard's segment (see §4.5). | `(0, 1]` |

Product terms `weight × severity × confidence × exposure` are **floats**; summation order is **canonical** (see §8).

### 4.2 Default weights (configurable, `HAZARD_WEIGHTS`)

These defaults mirror `03_ARCHITECTURE.md` §8 (`HAZARD_WEIGHTS=pothole:3,road_crack:2,damaged_road:2,obstacle:1,debris:1`).

| class | default weight |
|-------|---------------|
| `pothole` | 3.0 |
| `road_crack` | 2.0 |
| `damaged_road` | 2.0 |
| `obstacle` | 1.0 |
| `debris` | 1.0 |

### 4.3 Default severities (configurable, `RISK_SEVERITIES`)

| class | default severity |
|-------|-----------------|
| `pothole` | 0.80 |
| `damaged_road` | 0.70 |
| `obstacle` | 0.60 |
| `road_crack` | 0.50 |
| `debris` | 0.30 |

### 4.4 Confidence

Given the aggregated `Hazard.confidence_summary` (`04_DATA_MODEL.md` §7.11):

- **Default mode `max`:** `confidence(h) = max(detection.confidence)` over member detections — the hazard is as credible as its strongest observation.
- Optional mode `mean` (env `RISK_CONFIDENCE_MODE=mean`): `mean(detection.confidence)`.
- Confidence is **never** replaced, invented, or rounded to a band. YOLO confidence is *detection* confidence, not "road danger" (`MASTER_PROJECT_PROMPT.md` §15).

### 4.5 Exposure (default: segment-length ratio)

```
exposure(segment(h)) = length_m(segment(h)) / route_length_m
```

- Uses **authoritative segment/route lengths** from the routing provider (`02_TRD.md` §12–§13). Never fabricated.
- A hazard concentrated in a long segment (large share of the journey) contributes more than the same hazard in a short segment.
- Equivalent to a density-weighted formulation: score rises with both **hazard count** and **affected fraction of the route**.
- Alternative mode `hazard_density` (`RISK_EXPOSURE_MODE=hazard_density`) substitutes `count_in_segment / count_segments_pre_aggregation` (documented as a distinct configuration; see §10 — it MUST bump `configuration_version`).
- If `route_length_m ≤ 0` or a hazard's `segment_id` is missing/invalid → the engine returns `unavailable` (see §7). It never invents a length.

---

## 5. NORMALIZATION (EXACT)

Selected normalization function: **hyperbolic-tangent saturation**. Single function, fully deterministic.

```
# RISK ENGINE — NORMALIZATION (algorithm_version = v1.0)
# Input : raw       (from §4)
# Output: score     (0..100, stored at 2 decimals; integer for display)

const GAIN = config("RISK_NORMALIZATION_GAIN", default = 1.25)   # saturation scale
fraction  = tanh(raw / GAIN)          # monotonic, maps raw ∈ [0, ∞) → [0, 1)
score     = round(fraction * 100, 2)  # 2-decimal storage (numeric(5,2))
display   = round(score)              # integer shown in UI / cards
```

Properties:

- `tanh(0) = 0` ⇒ a **genuinely empty** hazard set scores exactly `0.00` (§6).
- Monotonic: more/stronger hazards never lower the score.
- Bounded: score can never exceed `100.00` regardless of hazard count or extreme inputs.
- Inverse is unnecessary at runtime; `atanh` is only used in calibration tests.

### 5.1 Calibration anchor (illustrative)

Default `GAIN = 1.25` is calibrated so the canonical worked example in this document (§11) reproduces the `risk_score = 28` used throughout the project docs (`02_TRD.md` §35, `03_ARCHITECTURE.md` §6.7). Exact calibration is a config concern — changing it bumps `configuration_version` (§10).

---

## 6. STATUS: `calculated` vs `unavailable`

Two statuses only (matches `04_DATA_MODEL.md` §7.15 enum and `07_API_CONTRACT.md` §7.12):

| `risk_status` | Meaning | `risk_score` |
|---------------|---------|--------------|
| `calculated` | The engine had valid aggregated hazards + geometry + config and computed a number.**May be `0.00` when the analysis genuinely found no hazards.** | numeric `0..100` |
| `unavailable` | The engine could not produce an authoritative number (no/no-useful hazard data, invalid geometry, config corruption, failure). | `NULL` |

**The "no-risk floor" is *not* a numeric constant applied on failure.** A floor of `0` is meaningful *only* as the result of a **successful** analysis that concluded "zero unique hazards present". It is **never** used to mask failure (`07_API_CONTRACT.md` §7.12: failure → `{ "risk": { "status": "unavailable" } }`).

---

## 7. EMPTY HAZARD SET & MISSING DATA HANDLING

The engine receives a hazard data completeness flag from the Hazard Aggregation stage (`hazard_analysis.status` in {`completed`, `partial`, `failed`}).

| Scenario | Decision |
|----------|----------|
| `completed`, 0 hazards, coverage ≥ `RISK_MIN_CONCLUSION_COVERAGE` (default `1.0`) | `calculated`, `risk_score = 0` — a genuine "no hazards detected in the analyzed imagery" conclusion. |
| `completed`, 0 hazards, coverage < minimum | `unavailable` — we may **not** claim "no hazards" on partial imagery (`MASTER_PROJECT_PROMPT.md` §11). |
| `completed`, ≥1 hazard | `calculated` (normalized score). If coverage < 1.0, expose `coverage_ratio` (see §11) so the UI discloses partial imagery. |
| `partial` (some segments analyzed, ≥1 hazard) | `calculated` over available data **with** `risk_status` still `calculated` but a disclosed `coverage_ratio < 1.0`; never `0`. Behavior configurable via `RISK_PARTIAL_MODE=degraded_calculated` (default) / `unavailable`. |
| `partial` or `failed`, no usable hazard data | `unavailable`, `risk_score = NULL`. Never `0`. |
| `failed` | `unavailable`. Log `RISK_INPUT_UNAVAILABLE` (`09_ERROR_HANDLING.md` §10.6). Never fabricate. |
| missing `confidence_summary` for any included hazard | input-integrity failure → `unavailable` (never default to a guessed confidence). |
| unknown class (not in active model class list) | startup configuration error; if encountered at runtime → `unavailable` + log `RISK_CONFIG_MISMATCH`. |
| `route_length_m ≤ 0` / missing hazard `segment_id` | `unavailable` (division-by-zero / fabrication guard). |

`coverage_ratio = segments_analyzed / segments_total` is always emitted in the risk payload (see §11) so the UI never presents a score without its coverage context (`02_TRD.md` §20: "Analyzed segments / Analyzed imagery").

---

## 8. DETERMINISM GUARANTEES

The engine guarantees byte-identical scores for identical inputs:

1. **No randomness** — no RNG, no sampling, no tie-breaking by insertion order.
2. **Canonical iteration order** — hazards sorted by `(segment.sequence, hazard_id)` before summation; classes map to a fixed weight table; rounding applied at exactly one point (§5).
3. **Fixed-precision float arithmetic** — IEEE-754 `double`; the same product term ordering (`weight × severity × confidence × exposure`) in all code paths; no platform-dependent vectorization in the scoring loop.
4. **Pure function** — no I/O, no wall-clock, no global mutable state, no threads inside `calculate_route_risk(...)` (`02_TRD.md` §31).
5. **Deterministic inputs** — the score is computed from the *stored* aggregated hazard rows + *stored* segment geometry, never from re-read external providers.
6. **Version-locked** — the resolved config snapshot is frozen per calculation; a later config change cannot retroactively alter stored scores.

Tests: run the same fixture through the engine twice (separate processes) and assert identical 2-decimal values; see §12 cases T10–T12.

---

## 9. REPRODUCIBILITY INPUTS

A stored `risk_analysis` row is fully reproducible when the following are preserved (matches `02_TRD.md` §66, §132, §163):

```
Route data            → route_id, segment geometry/lengths (authoritative routing output)
Image IDs             → road_images.image_id used in detection
Aggregated hazards    → hazard_id, hazard_type, confidence_summary, segment_id, member image_ids
Model version         → model_version_id (04_DATA_MODEL.md §7.13)
Risk configuration    → algorithm_version + configuration_version (+ frozen config snapshot/digest)
Timestamp             → calculated_at
```

Replay procedure: reload the same hazard rows, same lengths, resolve the same config snapshot, run §4→§5 → the stored `risk_score` must match exactly. Any mismatch is a defect (`09_ERROR_HANDLING.md` §10.6).

---

## 10. VERSIONING: `algorithm_version` + `configuration_version`

Two independent version axes, both persisted on every `RiskAnalysis` row (`04_DATA_MODEL.md` §7.15).

| Field | Meaning | MUST bump when |
|-------|---------|----------------|
| `algorithm_version` | Identity of the **formula and normalization function** (the code path: §4 + §5). | The math changes — e.g. tanh → clamp; summation changes; a class set is added to the formula. |
| `configuration_version` | Identity of the **resolved parameters** (weights, severities, gain, confidence/exposure modes, coverage thresholds, class list). | Any parameter changes — weights, severities, gain, thresholds. |

### 10.1 Semantics (worked example)

| State | algorithm_version | configuration_version | What changed |
|-------|-------------------|-----------------------|--------------|
| initial release | `v1.0` | `v1.0` | — |
| severity `pothole` 0.80 → 0.90 | `v1.0` | **`v1.1`** | configuration only |
| `HAZARD_WEIGHTS` pothole 3.0 → 4.0 | `v1.0` | **`v1.2`** | configuration only |
| normalization tanh → clamp | **`v2.0`** | `v2.0` (reset) | algorithm change |

Rules:

- A **weights/severity/calibration change never** bumps `algorithm_version`; it only bumps `configuration_version` (exactly the "v1.0 → weights change → v1.1" contract).
- A **formula/normalization change** bumps `algorithm_version` and resets `configuration_version` to match.
- Every released configuration is recorded (label + canonical JSON digest `sha256` of the frozen parameter set) so "which parameters ran" is as traceable as "which code ran".
- Historical rows keep their scores and their own version pair — old scores are never recomputed in place.

---

## 11. RISK SCORE COMPONENTS OUTPUT

Consistent with `02_TRD.md` §35 and persisted in `RiskAnalysis.weighted_components` (`04_DATA_MODEL.md` §7.15).

```
{
  "risk_score": 28,
  "risk_scale": "0-100",
  "risk_status": "calculated",
  "algorithm_version": "v1.0",
  "configuration_version": "v1.1",
  "hazard_count": 6,
  "coverage": { "images_analyzed": 15, "segments_analyzed": 24,
                "segments_total": 24, "coverage_ratio": 1.0 },
  "risk_components": {
    "potholes":     { "count": 3, "weighted_raw": 0.25500, "score_contribution": 19.5 },
    "road_cracks":  { "count": 2, "weighted_raw": 0.06667, "score_contribution":  5.1 },
    "damaged_road": { "count": 1, "weighted_raw": 0.04375, "score_contribution":  3.4 },
    "obstacle":     { "count": 1, "weighted_raw": 0.01875, "score_contribution":  0.0 },
    "debris":       { "count": 0, "weighted_raw": 0.00000, "score_contribution":  0.0 }
  }
}
```

- `score_contribution(class)` = final score allocated to that class **proportionally** to its `weighted_raw` share:

```
score_contribution(c) = score × ( weighted_raw(c) / Σ_c weighted_raw(c) )   # Σ == risk_score (rounding-adjusted)
```

  The allocation exists purely so the UI can explain "where the score came from" (`02_TRD.md` §20, `MASTER_RULES.md` §17); it is derived, never an independent score.
- `count`, `weighted_raw`, and confidence/exposure detail remain in the payload so the displayed score is always auditable.
- When `risk_status=unavailable`: `risk_score=null`; `risk_components` may be partially `null`/absent; UI shows the unavailable state, never `risk: 0` (`09_ERROR_HANDLING.md` §13).

---

## 12. BOUNDARY CONDITIONS & TEST CASES

Maps to the required risk tests (`02_TRD.md` §110, `05`-tier tests in `13_TESTING.md`).

| # | Case | Inputs | Expected `risk_status` | Expected `risk_score` | Expected `risk_components` / notes |
|---|------|--------|------------------------|-----------------------|------------------------------------|
| T1 | No hazards, full coverage | 0 hazards, coverage 1.0, valid geometry | `calculated` | `0.00` | all `count=0`, contributions 0 |
| T2 | No hazards, partial coverage | 0 hazards, coverage 0.5 | `unavailable` | `NULL` | must NOT say "no hazards" (`MASTER_PROJECT_PROMPT.md` §11) |
| T3 | One hazard, low confidence | 1 pothole, conf 0.51, exposure 0.5 | `calculated` | `≈ 45.45` | raw = 3×0.8×0.51×0.5 = 0.612 |
| T4 | One hazard, high confidence | 1 pothole, conf 0.95, exposure 1/24 | `calculated` | `≈ 7.59` | raw = 3×0.8×0.95×0.041667 ≈ 0.095 |
| T5 | Many hazards | 10 potholes conf 0.95, exposure 1/24 each | `calculated` | `≈ 64.0` | monotonic ↑ vs T4 |
| T6 | Maxed single hazard | 1 hazard weight 3.0, severity 1.0, conf 1.0, exposure 1.0 | `calculated` | `98.37` | tanh(3/1.25)×100 — bounded < 100 |
| T7 | Maxed hazard set | many maxed hazards | `calculated` | `< 100.00` (saturates) | never exceeds 0–100 bounds |
| T8 | Missing severity (class has none) | severity absent for a class | use default severity; deterministic | — | null severity ⇒ default, never invented |
| T9 | Unknown class | hazard class not in model class list | `unavailable` (runtime) / startup error | `NULL` | config mismatch; never guessed weight |
| T10 | Route length 0 / missing segment | `route_length_m ≤ 0` or dangling `segment_id` | `unavailable` | `NULL` | guard, no division by zero |
| T11 | Missing confidence | `confidence_summary` null on an included hazard | `unavailable` | `NULL` | input-integrity failure |
| T12 | Determinism | same fixture run twice, separate processes | `calculated` | byte-identical (2 decimals) | see §8 test |
| T13 | Version traceability | same hazards, config v1.0 vs v1.1 | both `calculated` | different scores, each with own version pair | never recompute history in place |

Calibration values in T3–T7 use `GAIN = 1.25` and default tables §4.2–4.3. Any table change is a configuration change (→ `configuration_version`, §10).

---

## 13. FAILURE BOUNDARIES

- **Never** `risk_score = 0` on: YOLO failure, no imagery, hazard-stage failure, provider failure, config error, timeout.
- Correct failure output (`07_API_CONTRACT.md` §7.12):

```json
{ "route_id": "route_1", "risk": { "score": null, "scale": "0-100",
                                   "algorithm_version": "v1.0", "status": "unavailable" } }
```

- A risk-engine failure **never destroys the route result** — route + facilities remain available; safety is flagged `unavailable` (`02_TRD.md` §49, §140–§141; `09_ERROR_HANDLING.md` §10.6). The pipeline state machine treats `RISK_CALCULATION` similarly to an optional stage (`04_DATA_MODEL.md` §7.23).
- The LLM must restate failure as failure; it must not "fill in" a risk number (§2 I5; `12_LLM_SPEC.md` §2).

---

## 14. CONSISTENCY WITH THE REST OF THE PROJECT

| Doc | Where this spec aligns |
|-----|------------------------|
| `07_API_CONTRACT.md` §7.12 | `risk.score`, `risk.scale="0-100"`, `risk.algorithm_version`, `risk.status` enum `calculated|unavailable`; failure ⇒ `score:null` not `0`. |
| `04_DATA_MODEL.md` §7.15 | `risk_score numeric(5,2) 0..100|null` (null ⇔ `unavailable`); `algorithm_version`, `configuration_version`, `hazard_count`, `weighted_components`, `exposure_metrics`, `status`, `calculated_at` all populated by this engine. |
| `04_DATA_MODEL.md` §7.16 | Traceability chain ends at this engine's versioned output. |
| `03_ARCHITECTURE.md` §6.7 | Same formula and payload shape (`risk_score`, `hazard_summary`, `images_analyzed`, `segments_analyzed`, `model_version`); example `28` reproduced in §11. |
| `09_ERROR_HANDLING.md` §10.6 | `risk_status=unavailable` on missing inputs, never `score=0`. |
| `13_TESTING.md` | T1–T13 above are the risk engine test suite. |

---

## 15. CONFIGURATION SUMMARY

All parameters are externalized (`MASTER_RULES.md` §24). Defaults below; resolved snapshot is frozen + digested per calculation (§10).

| Variable | Default | Purpose |
|----------|---------|---------|
| `HAZARD_WEIGHTS` | `pothole:3,road_crack:2,damaged_road:2,obstacle:1,debris:1` | per-class weights (§4.2) |
| `RISK_SEVERITIES` | `pothole:0.8,damaged_road:0.7,obstacle:0.6,road_crack:0.5,debris:0.3` | per-class severities (§4.3) |
| `RISK_CONFIDENCE_MODE` | `max` | aggregated confidence: `max` or `mean` (§4.4) |
| `RISK_EXPOSURE_MODE` | `segment_length_ratio` | exposure definition (§4.5) |
| `RISK_NORMALIZATION_GAIN` | `1.25` | tanh saturation gain (§5) |
| `RISK_MIN_CONCLUSION_COVERAGE` | `1.0` | min `coverage_ratio` to conclude "no hazards" (§7) |
| `RISK_PARTIAL_MODE` | `degraded_calculated` | partial-coverage behavior (§7) |

---

## 16. LIMITATIONS

- The score reflects **available imagery and the trained dataset**; stale/absent imagery may make the result `unavailable` or degraded — never inflated (§7, `02_TRD.md` §136).
- `confidence` is detection confidence, not probability of a real-world hazard (`MASTER_PROJECT_PROMPT.md` §15).
- A low score is **not** "completely safe" (`02_TRD.md` §138); a high score is not a guarantee of harm. The metric is comparative/analytic only.
- Scoring is per-route; facilities are never folded in (§1).

---

# END OF RISK ENGINE SPECIFICATION