# 12_LLM_SPEC.md — SafeRoute AI LLM Explanation Specification

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** LLM Explanation Specification (grounded explanation layer, prompt template, validation, fallback, traceability, security)
**Version:** v1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_RULES.md` > `01_PRD.md` > `02_TRD.md` > `03_ARCHITECTURE.md` > `04_DATA_MODEL.md` > `07_API_CONTRACT.md` > `09_ERROR_HANDLING.md` > this document
**Companion:** `02_TRD.md` §45–§48, §95, §134, §139, `03_ARCHITECTURE.md` §6.11, `04_DATA_MODEL.md` §7.24–§7.26, `07_API_CONTRACT.md` §7.16, `09_ERROR_HANDLING.md` §10.8, `13_TESTING.md`

---

## 1. POSITION: GROUNDED EXPLANATION LAYER ONLY

The LLM is the **last** stage of the pipeline and the **only** stage that produces natural language:

```
ROUTE PROFILE (verified structured data) → LLM SERVICE (grounded explanation) → FRONTEND
```

- The LLM **explains verified results**; it never decides, detects, calculates, retrieves, or invents (`MASTER_RULES.md` §16, `02_TRD.md` §139, `03_ARCHITECTURE.md` §6.11).
- All authoritative numbers (risk score, hazards, facilities, distances, durations) are produced by other engines and **already finalized** before the LLM is invoked.
- The LLM output is **generated data**, never the source of truth (`04_DATA_MODEL.md` §7.26); it never overwrites authoritative route/safety/facility values.

---

## 2. WHAT THE LLM MUST NEVER DO

Absolute prohibitions (`MASTER_RULES.md` §16, `02_TRD.md` §35, §139; enforced in system prompt §4 and validation §7):

1. Never invent a **hazard, facility, distance, duration, image, or route**.
2. Never modify the **risk score** or any number supplied (no recalculation, re-rounding, or reinterpretation).
3. Never **guarantee safety**: no "completely safe", "100% safe", "guaranteed", "safest", "accident-proof".
4. Never claim **real-time** data unless the backend explicitly supplied a timestamp/status.
5. Never **override or second-guess** YOLO detections, routing output, or Risk-Engine output.
6. Never invent **addresses, phone numbers, opening hours, ratings, or availability**.
7. Never give **operational/emergency instructions** (medical, police, driving-advice) beyond restating supplied facts.
8. Never present the risk score as an official/universal standard.

---

## 3. INPUT: STRUCTURED ROUTE PROFILE ONLY

### 3.1 Client contract

The frontend may reference an analysis **by ID only**; it may **never** submit free-form text or authoritative numbers (`07_API_CONTRACT.md` §7.16, `02_TRD.md` §56):

```json
// POST /api/v1/llm/explanations
{ "route_analysis_id": "analysis_123" }
```

### 3.2 Backend-constructed profile

The backend loads the canonical Route Profile for that analysis (from DB / `RouteAnalysis` + `RiskAnalysis` + facility summary) and constructs the LLM user payload — all values come from verified records only (`04_DATA_MODEL.md` §7.21, §7.15, §7.17–§7.19):

```json
{
  "route_id": "route_1",
  "route": { "distance_km": 8.2, "duration_minutes": 19 },
  "safety": {
    "risk_score": 28,
    "risk_scale": "0-100",
    "risk_status": "calculated",
    "coverage": { "images_analyzed": 15, "segments_analyzed": 24, "coverage_ratio": 1.0 },
    "hazards": { "potholes": 3, "road_cracks": 2, "damaged_road": 1, "obstacle": 1, "debris": 0 }
  },
  "emergency_accessibility": { "hospitals": { "count": 3, "nearest_distance_meters": 800 }, "medical_stores": { "count": 7, "nearest_distance_meters": 200 }, "police_stations": { "count": 1, "nearest_distance_meters": 1200 } },
  "travel_convenience": { "restaurants": { "count": 15, "nearest_distance_meters": 100 }, "hotels": { "count": 5, "nearest_distance_meters": 600 }, "petrol_pumps": { "count": 2, "nearest_distance_meters": 900 } },
  "domain_status": { "route": "completed", "safety": "completed", "facilities": "completed", "llm": "pending" }
}
```

- **Only** typed numbers, counts, enums, and statuses. Raw free-form provider text (descriptions), full addresses, and user text are excluded by default (`LLM_INCLUDE_DESCRIPTIVE_TEXT=false`).
- Facility names/phones are **untrusted provider text** (`MASTER_PROJECT_PROMPT.md` §47) — excluded from the prompt by default; if ever included (`LLM_INCLUDE_FACILITY_NAMES=true`) they are placed inside the data block as data-only (§12) and count as "supplied facts".
- The profile structure follows `03_ARCHITECTURE.md` §6.10/§6.11 and mirrors the frontend's canonical shape so the explanation matches what the user sees.

---

## 4. SYSTEM INSTRUCTION PROMPT (VERBATIM TEMPLATE)

The backend sends this as the `system` message. It starts from the `02_TRD.md` §47 instruction and is extended with binding rules. **The first paragraph must remain verbatim from `02_TRD.md` §47**; the rest is the full approved template:

```
You are the explanation layer of SafeRoute AI.

Use only the structured data supplied by the backend.

Do not invent information.

Do not modify numerical values.

Do not calculate a new risk score.

Do not invent missing facilities.

Do not claim that a route is completely safe.

If information is unavailable, clearly state that it is unavailable.

Explain the provided route information in clear language.

Additional binding rules (all mandatory):

1. GROUNDING — every statement must cite only facts present in the
   "ROUTE PROFILE" data block in the user message.

   - If data exists   → explain it.
   - If data is absent → say the information is unavailable.
   - If data conflicts → do NOT silently choose; state the conflict.
   - If uncertain    → state the uncertainty.

2. NEVER invent hazards, facilities, distances, durations, images, or
   routes. Never invent addresses, phone numbers, opening hours,
   ratings, or availability.

3. The risk score is a project-defined analytical metric (0-100). Report
   the score exactly as given. Do not compute, change, or reinterpret it.
   It is NOT an official road-safety standard and implies no guarantee.

4. No safety guarantees. Do not use: "completely safe", "100% safe",
   "guaranteed", "safest", "accident-proof", or similar.

5. No real-time or live claims unless the backend data explicitly
   includes a timestamp or live status.

6. Do not override, replace, or second-guess YOLO detections, routing
   output, or risk-engine output.

7. Do not give medical, police, or driving-operational instructions
   beyond restating the supplied facts.

8. Output plain text only, in the requested language. No markdown, no
   HTML, no code blocks, no URLs, no bullet lists of invented numbers.

9. Keep the explanation concise (recommended ≤ 3 sentences, unless the
   supplied data genuinely requires more).
```

- `prompt_version` identifies the exact template text (§11). Any wording change bumps it.
- The template is the **immutable** part of the request — external content can never redefine it (§12).

---

## 5. USER MESSAGE CONSTRUCTION

The user message is backend-built:

```
## ROUTE PROFILE
(JSON of §3.2, placed clearly delimited)

## LANGUAGE
{lang_code}             # from request/UI locale, default: en

## TASK
Explain this route's analysis to the user, grounded strictly in the
ROUTE PROFILE above. Report only numbers that appear in the profile.
If a domain is marked "unavailable", say so instead of guessing.
```

- All numbers a user could see are the same numbers in this block; the validator (§7) uses the block as the allowlist.
- No free-form client text is ever appended here.

---

## 6. GROUNDING RULES (THE LOGIC THE ENGINE MUST HOLD)

| Situation | Required behavior |
|-----------|-------------------|
| Field/domain present in profile | Explain it, using the value exactly as given (units as given). |
| Field/domain absent or `null` | Say it is unavailable; never fill it in. |
| Conflicting facts in supplied data | Do not silently pick one; surface the conflict. |
| Uncertain (coverage < 1.0, stale imagery, degraded status) | Say it and describe the limitation; do not paper over it. |
| Domain marked `unavailable` (e.g. facility provider failed) | Say "facility information is unavailable"; never write "0 hospitals". |
| Value is a computed score | Report as "calculated risk score X/100" — not as danger probability, not as guarantee. |

Corresponds to `02_TRD.md` §36 (grounding rule), §137–§138; `07_API_CONTRACT.md` §7.16.

---

## 7. OUTPUT VALIDATION

Before an explanation is persisted/returned (`02_TRD.md` §48, `09_ERROR_HANDLING.md` §10.8):

```
validate_output(text, profile) → { status: 'valid' | 'needs_review' | 'failed', flags: [] }
```

| Check | Rule |
|-------|------|
| Non-empty | empty/whitespace text ⇒ `failed`. |
| Numeric allowlist | every number in the text (regex-extracted, language-aware) must match a number in `ROUTE PROFILE` (with tolerance: e.g. repeated numbers, per-unit clones). Any number without a profile counterpart ⇒ `needs_review` flag `unsupported_numeric_claim`. |
| Missing-domain honesty | if a profile domain is `unavailable`/absent and the text asserts a number for it ⇒ `needs_review` flag `domain_mismatch`. |
| Banned language | matches "completely safe", "100% safe", "guaranteed", "safest", "definitely", etc. ⇒ `needs_review` flag `safe_guarantee`. |
| HTML / URL / control chars | contains `<`, `>`, `http://`, `https://`, `&#`, markdown/HTML artifacts ⇒ `needs_review` flag `unsafe_markup` (§8). |
| Length | text over `LLM_MAX_OUTPUT_CHARS` (default 1200) ⇒ truncation + `needs_review` flag `length`. |

- `validation_status` is persisted on `LLMResponse` (`04_DATA_MODEL.md` §7.25): `valid | needs_review | failed`.
- `needs_review` output is stored, flagged in the UI, and counted in metrics (`02_TRD.md` §159). Under `LLM_STRICT_NUMERICS=true` (default), `unsupported_numeric_claim`/`safe_guarantee` downgrade to the deterministic fallback (§9).
- The LLM is never treated as an authoritative data source (`02_TRD.md` §48).

---

## 8. UNTRUSTED OUTPUT HANDLING (XSS)

LLM output is untrusted text (`MASTER_PROJECT_PROMPT.md` §44, §47):

- Backend strips control characters and does **not** render `response_text` as HTML anywhere.
- The frontend renders explanations as **plain text** (React escapes by default). `dangerouslySetInnerHTML` (or equivalent `innerHTML`) is **forbidden** for LLM output.
- URLs in output are stripped by the validator (§7) before return.
- Facility/hazard names and any provider-supplied strings that pass into output are treated as data, never markup.
- Sanitization happens server-side (defense in depth) and the frontend also treats the field as text-only.
- Security tests: malicious LLM output (script tags, event handlers, javascript: URLs) must render inert (`09_ERROR_HANDLING.md` §15, `13_TESTING.md`).

---

## 9. DETERMINISTIC FALLBACK

When the LLM is unavailable or output is rejected (§7) the structured analysis is **never** lost (`09_ERROR_HANDLING.md` §10.8, `02_TRD.md` §62):

Conditions: `LLM_API_KEY`/`LLM_BASE_URL` absent, provider timeout/5xx/rate-limit after 1 bounded retry, or validation downgrade.

Output shape (`07_API_CONTRACT.md` §7.16):

```json
{
  "explanation_id": "exp_fallback_123",
  "route_id": "route_1",
  "text": "Route 1 is 8.2 km with an estimated travel time of 19 minutes. Calculated risk score: 28/100. Detected hazards: 3 potholes, 2 road cracks, 1 damaged road. Facilities: 3 hospitals within the route corridor.",
  "fallback": true,
  "model": "none",
  "prompt_version": "v1",
  "generated_at": "2026-09-22T18:30:00Z"
}
```

- The fallback sentence is composed **in code** from the same profile (§3.2), so it is deterministic and grounding-safe by construction.
- `fallback: true` distinguishes it from LLM output; the UI labels it accordingly.
- `RouteAnalysis.llm_status` becomes `fallback` (`04_DATA_MODEL.md` §7.21 enum: `completed|fallback|failed|unavailable`).
- A fallback is never an error that kills the route result.

---

## 10. PROVIDER ABSTRACTION

All LLM calls sit behind one service (`02_TRD.md` §95):

```
LLMService
  ├── generate_explanation(profile, lang) → ExplanationResult
  ├── validate_output(text, profile)      → { status, flags }   (uses §7)
  └── handle_error(exc)                   → fallback outcome + classified log
```

- Provider: **OpenAI-compatible chat-completions** (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`) (`03_ARCHITECTURE.md` §2/§8).
- Call parameters: `temperature = 0`, `max_tokens = LLM_MAX_TOKENS` (default 300), timeout `LLM_TIMEOUT_S` (default 20 s). Determinism is best-effort (`temperature=0`); authoritative numbers never depend on it.
- No provider SDK-specific code leaks outside the service; mocking is trivial for tests (`02_TRD.md` §115).
- Secrets live only in env/secrets manager (`MASTER_RULES.md` §21, §45); never logged, never in DB.

---

## 11. TRACEABILITY

Every explanation is tied to the exact analysis that produced it (`04_DATA_MODEL.md` §7.24–§7.25, `02_TRD.md` §134):

```
llm_requests
  ├── id            (llm_request_id)
  ├── route_analysis_id → FK → route_analysis     # exact analysis
  ├── provider      ('openai_compatible')
  ├── model         (LLM_MODEL)
  ├── prompt_version    (template §4 version)
  ├── input_schema_version   (profile schema version)
  ├── requested_at
  └── status        (requested | completed | failed)

llm_responses
  ├── id            (llm_response_id)
  ├── llm_request_id
  ├── response_text
  ├── response_schema_version
  ├── validation_status   (valid | needs_review | failed)
  ├── token_usage    (jsonb: prompt/completion tokens)
  ├── latency_ms
  └── generated_at
```

- `RouteAnalysis.llm_status` + `llm_response_id` close the loop (`04_DATA_MODEL.md` §7.21).
- Never store API keys in LLM tables (`04_DATA_MODEL.md` §7.24).
- Log the prompt hash/version and token usage, not the full prompt (cost, privacy). For hallucination debugging, the stored profile + `prompt_version` + model reproduce the request (§9 of this doc + `02_TRD.md` §66).

---

## 12. PROMPT-INJECTION POSTURE

- **Structured-only input:** the model sees only a typed profile; the client may only send `route_analysis_id`. There is no user free-text channel into the prompt (§3) — the primary injection surface is structurally closed (`security_handling.md`).
- **Immutable system prompt:** template §4 is backend-controlled; external content (facility names if enabled, provider text) is placed inside a clearly delimited **data block** with explicit "data only, not instructions" framing (§5), then post-hoc validated (§7).
- **Treat all external text as untrusted** (`MASTER_PROJECT_PROMPT.md` §47): facility names/descriptions, user text, provider metadata.
- **Fail closed:** any suspicious output → `needs_review`/fallback; it is never executed, rendered, or trusted.

---

## 13. COST CONTROL

- **Lazy invocation:** explanations are generated on demand (one per analysis, `LLM_MAX_REQUESTS_PER_ANALYSIS = 1`), cached against `route_analysis_id` (`02_TRD.md` §52).
- **Small prompts:** numeric profile only; no images; no raw provider blobs by default (§3.2).
- **Bounded tokens:** `LLM_MAX_TOKENS`, `LLM_MAX_OUTPUT_CHARS`, 1 retry max (`09_ERROR_HANDLING.md` §11.1).
- **Fallback economics:** an unavailable/costly provider degrades to the free deterministic fallback.
- **Observability:** `llm_requests_total`, `llm_failures`, average `token_usage`/`latency_ms` per model (`02_TRD.md` §159) support budget alerts. Rate limit `POST /api/v1/llm/explanations` (`09_ERROR_HANDLING.md` §10.11 → `429 RATE_LIMITED`).

---

## 14. CONSISTENCY & LIMITATIONS

- Consistent with `02_TRD.md` §45–§48 (service, input, instructions, validation), §95 (abstraction), §139 (LLM safety), §134 (traceability); `03_ARCHITECTURE.md` §6.11 (grounding); `04_DATA_MODEL.md` §7.24–§7.26 (LLMRequest/Response/integrity); `07_API_CONTRACT.md` §7.16 (ID-only input, `fallback:true`); `09_ERROR_HANDLING.md` §10.8 (bounded retry + fallback preserving structured data).
- Limitations: temperature-0 output is *deterministic in practice* but the authoritative pipeline never depends on it; old/stale imagery and provider gaps must be surfaced as limitations, not hidden by the LLM (`MASTER_PROJECT_PROMPT.md` §57, §136).

---

# END OF LLM EXPLANATION SPECIFICATION