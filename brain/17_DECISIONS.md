# 17_DECISIONS.md — SafeRoute AI Decisions (ADR Log)

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Architecture Decision Record (ADR) Log
**Version:** 1.0
**Status:** Active
**Format:** Latest decision first. Each entry: Status, Context, Decision, Consequences.

Architecture decisions are recorded so future changes preserve the documented rationale. A decision is superseded only by a new ADR that explicitly states it supersedes the older one.

---

## ADR-006 — Provider stack fixed: OSRM + Overpass + OpenAI-compatible LLM + YOLO11/ultralytics

- **Status:** Accepted
- **Context:** SafeRoute AI needs routing, nearby-facility discovery, road-hazard detection, and natural-language explanation. Several commercial providers require API keys and cost money per call, which is undesirable for a keyless, low-cost college production. Any provider may change later, so the system must not be coupled to a single vendor.
- **Decision:** Fix the provider stack as defaults behind abstractions (`03_ARCHITECTURE.md` §2, §6): OSRM for routing (keyless public API, self-hostable later), Overpass API over OpenStreetMap for facilities (keyless), an OpenAI-compatible chat-completions API for the LLM (`LLM_BASE_URL` + `LLM_API_KEY`, degrading gracefully when absent), and YOLO11 via `ultralytics` for hazard detection.
- **Consequences:** No routing/facility API keys needed, keeping cost low. Each provider sits behind an internal abstraction (`RoutingService`, `FacilityService`, `LLMService`, YOLO inference service) so it can be replaced without rewriting the system (`02_TRD.md` §93–§95). Capability differences (e.g., OSRM alternatives count, Overpass freshness, LLM latency) must be handled as partial/unavailable states (`09_ERROR_HANDLING.md`). Provider terms and licensing must be reviewed before commercial deployment (`MASTER_PROJECT_PROMPT.md` §89–§91).

---

## ADR-005 — Risk and facilities are never merged into one "AI safety score"

- **Status:** Accepted
- **Context:** It is tempting to combine hazards, hospitals, restaurants, petrol, hotels, and police stations into a single headline "AI Safety Score". That produces an opaque number that conflates road conditions with neighboring services and can mislead users into believing more restaurants means a safer road (`MASTER_PROJECT_PROMPT.md` §28).
- **Decision:** Adopt the MIRE-style separation contract: Road Safety (risk score/hazards), Emergency Accessibility (hospitals, medical stores, police stations), Travel Convenience (restaurants, hotels, petrol pumps), and Route Information (distance, duration) are separate dimensions and are never summed into one arbitrary score (`MASTER_RULES.md` §14, `07_API_CONTRACT.md` §10, `03_ARCHITECTURE.md` §6.9).
- **Consequences:** The UI keeps separate dimensions/chips instead of one "safety percentage" (`08_UI_SPEC.md` §11–§12). The LLM explains each dimension from verified data and never manufactures a combined score. This prevents a misleading single "AI safety score" and keeps every metric explainable and traceable. The downside: no single headline metric for quick decisions — accepted in favor of transparency.

---

## ADR-004 — LLM is an explanation layer only; never authoritative numbers

- **Status:** Accepted
- **Context:** The community/industry risk is that generative AI appears authoritative. If the LLM computes or restates risk, hazards, distances, or facility counts, it can hallucinate numbers and undermine the deterministic risk engine, and it could claim a route is safe.
- **Decision:** The LLM receives only the verified structured Route Profile and produces natural-language explanation. It never calculates the risk score, never modifies verified data, never invents hazards/facilities/distances/routes, never fills missing data with guesses, and never guarantees safety (`MASTER_RULES.md` §16, `MASTER_PROJECT_PROMPT.md` §34–§37). Risk is always computed by the deterministic risk engine (`03_ARCHITECTURE.md` §6.7). When the LLM fails (or key is absent), a deterministic fallback sentence is returned and the structured analysis remains intact (`09_ERROR_HANDLING.md` §10.8).
- **Consequences:** LLM output is presented as AI-generated text, and structured data remains authoritative (`MASTER_PROJECT_PROMPT.md` §77). Prompt-injection defenses and output validation are required (`02_TRD.md` §48, `security_handling.md` §12). Users always have the verified numbers alongside the explanation.

---

## ADR-003 — Async analysis via FastAPI BackgroundTasks; no Celery/message queue in v1

- **Status:** Accepted
- **Context:** Route analysis (image collection → OpenCV → YOLO → aggregation → risk → facilities → LLM) can take longer than a synchronous request comfortably allows. Message queues/worker clusters add operational complexity inappropriate for a college project's actual workload (`MASTER_RULES.md` §27).
- **Decision:** Use FastAPI `BackgroundTasks` (Python `asyncio`) for async analysis job execution in v1 (`03_ARCHITECTURE.md` §2). `POST /routes/{id}/analysis` schedules a job; clients poll `GET /api/v1/jobs/{id}` for status `queued/processing/partial/completed/failed` (`02_TRD.md` §82–§84, `07_API_CONTRACT.md` §7.7).
- **Consequences:** No infrastructure to operate beyond the backend process; fast to build and debug. BackgroundTasks are not durable across restarts and do not scale horizontally beyond the process — acceptable for v1 scale. Revisit with a message queue (Celery/RQ) only when measured workload demonstrates a requirement, not speculatively.

---

## ADR-002 — Dynamic 1–4 routes; never pad; no hard-coded Route A/B

- **Status:** Accepted
- **Context:** Provider-dependent route availability varies: 1, 2, 3, or 4 alternatives may be returned. Hard-coding "Route A / Route B / Route C / Route D" or fabricating routes to reach four would break the no-fabrication rule and mislead users.
- **Decision:** Candidate routes are a dynamic collection (`routes: [route_1 … route_n]`, `1 ≤ n ≤ MAX_CANDIDATE_ROUTES` = 4). The system displays exactly what the routing provider returns; it never pads, invents, or renames routes to reach four (`MASTER_PROJECT_PROMPT.md` §7, `03_ARCHITECTURE.md` §5).
- **Consequences:** All UI, data model, risk, facility, and profile logic must handle 1–4 routes uniformly without assuming exactly four (`02_TRD.md` §5, §10). Each route keeps a unique `route_id`; UI must handle fewer than four route cards and "No route available" (`MASTER_RULES.md` §6, §10).

---

## ADR-001 — No user accounts in v1; public rate-limited endpoints; auth later

- **Status:** Accepted, with an open follow-up marked `[DECISION REQUIRED]`
- **Context:** User accounts, sign-in, and per-user history add significant scope (auth flows, password handling, privacy, JWT management, recovery) that is not required for v1 route analysis. Public endpoints risk abuse.
- **Decision:** v1 ships public, rate-limited API endpoints subject to abuse prevention (`MASTER_PROJECT_PROMPT.md` §107–§108, `07_API_CONTRACT.md` §8). No user accounts, no stored user locations, no per-user history in v1. A `users` entity remains optional/skippable (`02_TRD.md` §60, `04_DATA_MODEL.md` §7.1).
- **Consequences:** Simpler privacy posture (no PII retention) and less scope. Public abuse is controlled by rate limiting, request size limits, and validation. When authenticated features (saved routes, feedback) are requested later, they require an auth design decision: local accounts vs OAuth provider, token strategy, and retention policy. **`[DECISION REQUIRED]`: authentication approach for post-v1 user-facing features — to be made before introducing accounts or personalized features.**

---

# END OF ADR LOG