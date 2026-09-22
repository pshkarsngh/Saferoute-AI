# security_handling.md — SafeRoute AI Security Specification

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Authoritative Security Specification (alias: `10_SECURITY.md`)
**Version:** 1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_RULES.md` > `01_PRD.md` > `02_TRD.md` > `03_ARCHITECTURE.md` > `07_API_CONTRACT.md` > `09_ERROR_HANDLING.md` > this document
**Companion:** `04_DATA_MODEL.md`, `05_DATA_SOURCES.md`, `06_SCRAPING_SPEC.md`, `08_UI_SPEC.md`, `09_ERROR_HANDLING.md`, `runbooks/credential-reevocation-or-leak.md`

Any unresolved security decision is marked `[DECISION REQUIRED]` with options, security implications, and affected documents.

---

## 1. PROJECT CONTEXT

SafeRoute AI generates up to 4 candidate routes from a source + destination, then analyzes each route through road imagery → OpenCV → YOLO11 → hazard aggregation → deterministic risk → facility discovery → Route Profile → grounded LLM explanation, displayed in a frontend.

**Security-relevant invariants:**
- The LLM is an explanation layer only: it never replaces routing/OpenCV/YOLO11, never calculates the risk score, never modifies verified backend data, and never invents hazards/facilities/distances/geometry/confidence, and never claims safety guarantees.
- Road Safety, Emergency Accessibility, Travel Convenience, and Route Information are separate dimensions — never merged into one opaque metric.
- Hazard classes come from the actual dataset/model config; facility categories: hospital, medical_store, restaurant, hotel, petrol_pump, police_station.
- **Unavailable data is never fabricated as zero** (enforced by `MASTER_RULES.md` §23, `09_ERROR_HANDLING.md`).

---

## 2. DOCUMENT AUTHORITY

This document is the **authoritative security specification**. It remains consistent with MASTER_RULES, PRD, TRD, Architecture, Data Model, Data Sources, API Contract, UI Spec, Error Handling, Testing, Deployment, Monitoring.

- If another document already defines a security requirement, preserve it.
- On conflict: identify it, use the higher-level project rule, and mark unresolved decisions `[DECISION REQUIRED]`.
- No new architecture is silently created here.

---

## 3. SECURITY OBJECTIVES

| Objective | SafeRoute AI meaning |
|-----------|----------------------|
| Confidentiality | Protect user data, credentials, tokens, private configuration, and internal infrastructure info |
| Integrity | Prevent unauthorized modification of routes, hazard detections, risk calculations, facility info, model config, analysis results |
| Availability | Resist abuse/attacks that make route analysis unavailable |
| Authenticity | Verify users, services, model artifacts, and external responses where appropriate |
| Authorization | Allow access only to what each user/service is permitted |
| Accountability | Trace actions to actors via request IDs + audit logging |
| Privacy | Minimize collection/retention of location and personal data |
| Resilience | Continue serving valid data during subsystem failures |
| Model integrity | Keep the YOLO11 artifact authentic, versioned, immutable |
| Data integrity | Keep provider, detection, and analysis data untampered |
| AI output integrity | LLM output is untrusted, validated, and never authoritative |

---

## 4. SECURITY PRINCIPLES

Secure by default · Least privilege · Defense in depth · Zero trust between services · Fail securely · Never trust client input · Never trust external API responses · Never trust uploaded files · Never trust LLM output · Never expose secrets · Minimize data collection · Minimize data retention · Explicit authorization · Strong input validation · Output encoding · Dependency minimization · Secure configuration · Auditability · Reproducibility · Traceability · Secure error handling.

---

## 5. THREAT MODEL

### Assets
User accounts & credentials, sessions/tokens, route requests/history, source/destination coordinates, road images (incl. uploaded), YOLO11 model + weights, dataset, hazard detections, risk configuration, facility data, database, API keys, LLM credentials, routing/facility provider credentials, storage credentials, logs, monitoring data, infrastructure config, CI/CD credentials.

### Actors (varying capability — not all equal)
Unauthenticated internet users · malicious authenticated users · automated bots · abusive API clients · compromised third-party providers · malicious file uploaders · prompt-injection attackers · supply-chain attackers (compromised dependencies) · tooling/CI compromise · insiders with excessive privileges.

### Key threat → mitigation map

| Threat | Attack surface | Primary mitigations | Residual risk |
|--------|----------------|---------------------|---------------|
| Secret leak | repo, logs, CI, frontend bundle | secrets manager, env injection, scanning, gitignore | low (human error) |
| API abuse / DDoS | public endpoints | rate limiting, request limits, quotas, WAF | low–med |
| Input injection (SQL/NoSQL/OS) | API params | typed schema validation, parameterized queries, no shell eval | low |
| File-based attack | image upload | MIME+decode+size validation, sandboxed processing | low–med |
| Prompt injection / LLM abuse | LLM service | grounding-only inputs, untrusted-output handling, no sys-context attacks | medium |
| Model tampering / swapped weights | model artifacts | signed/checksummed artifacts, versioned immutable store | low |
| Provider data spoofing | provider adapters | schema validation + provenance at boundary | low–med |
| XSS (esp. LLM/facility text) | frontend rendering | encode, sanitize, never render LLM as HTML | low |
| Supply chain | dependencies | lockfiles, CVE scan, pinning, minimal deps | low–med |
| Insider/privilege abuse | internal tooling | least privilege, audit, separation of duties | low |
| Data exposure via logs | logging | never-log list, redaction, retention policy | low |

---

## 6. ATTACK SURFACE

```
Browser → Frontend → API → Auth → Route Service → External Routing Provider
API → Image Service → Storage
Image Service → OpenCV → YOLO11
API → Facility Service → External Facility Provider
API → Risk Engine
API → LLM Service → External LLM Provider
All Services → Database → Logging / Monitoring
CI/CD → Deploy Pipeline → Infrastructure (env vars, containers)
```

Each hop above is a trust boundary: validate, authenticate/authorize, and limit what crosses it.

---

## 7. AUTHENTICATION & AUTHORIZATION

- **v1 (per PRD/TRD): no user accounts.** Public route-analysis endpoints do not require authentication.
- If authentication is added later (`[DECISION REQUIRED]`), use: hashed passwords (argon2/bcrypt) — never plaintext; short-lived sessions/tokens; refresh rotation; MFA optional; rate-limited login.
- **Authorization levels (even with no user accounts):**

| Area | Level |
|------|-------|
| Route generation/analysis/facilities/LLM | Public (v1), rate-limited |
| Image upload | Public + validated + rate-limited |
| Model management, system config, admin | Admin/Internal API key |
| YOLO inference / Risk Engine / facility adapter | Internal-only |

- **Least privilege:** internal services get scoped keys; no single key unlocks everything.
- **Never** expose internal ML/admin endpoints publicly.

---

## 8. API SECURITY

- **Validation:** Pydantic/typed schemas; coordinate ranges (`lat [-90,90]`, `lon [-180,180]`), enum allowsets (categories, statuses), request size limits (`07_API_CONTRACT.md` §7, `09_ERROR_HANDLING.md` §8).
- **Rate limiting:** 429 + `Retry-After` on route generation, analysis, image upload, LLM (`07_API_CONTRACT.md` §11.8).
- **CORS:** restrict origins to approved frontend(s); no wildcard with credentials.
- **CSRF:** not applicable to token-based/JSON APIs; revisit if cookies/auth added `[DECISION REQUIRED]`.
- **Headers:** CORS, CSP, `X-Content-Type-Options: nosniff`, `X-Frame-Options`, HSTS (TLS only).
- **Error responses:** standardized envelope; no stack traces, no internals (`09_ERROR_HANDLING.md` §9).
- **Injection:** parameterized DB access, no OS command construction from input, output encoding in UI.
- **Secrets in API:** never in URLs/logs/responses; headers/env only.

---

## 9. DATA PROTECTION (PII, Location, Retention)

- **Minimize collection:** PRD v1 collects only transient source/destination coordinates required for analysis (`02_TRD.md` §20.5). No PII by design.
- **Location data:** processed only for required functionality; not stored beyond analysis need unless required `[DECISION REQUIRED]`.
- **Encryption at rest** for database and object storage (TLS in transit everywhere, incl. provider calls).
- **Retention policy:** images lifecycle per `02_TRD.md` §77; configurable deletion; analysis data retained for reproducibility/audit.
- **No** personal data in logs, screenshots, or error responses.

---

## 10. ML & MODEL SECURITY

- **Artifact integrity:** model artifact stored outside git (`ml/models/` gitignored); record checksum/hash + version in `ModelVersion` (`04_DATA_MODEL.md` §7.13).
- **Authenticity:** load from pinned/versioned location; reject if hash mismatch or `model_version` missing.
- **Versioning:** never silently swap models; each detection row carries `model_version_id` (traceability).
- **Dataset security:** annotated data from permitted sources only; licensing documented in `docs/AI_MODELS.md`; no fabricated statistics.
- **Inference isolation:** YOLO runs as internal service; CPU/GPU resource caps; no arbitrary code path from untrusted input (image decode is the ML input vector — validate first, OpenCV before model).
- **Adversarial images:** images are validated (decode, size, quality) before inference; treat malformed media as invalid, never as no-hazard `[DECISION REQUIRED]` for deeper adversarial defenses if scare-resources exist.

---

## 11. IMAGE & FILE SECURITY

- Upload (only if in scope per PRD): validate MIME, extension, file size (`IMAGE_MAX_SIZE`), image decode, dimensions, content (`02_TRD.md` §76). Never trust extension alone.
- Store processed/analyzed images in object storage; DB holds references only (`04_DATA_MODEL.md` §7.6).
- Sandbox/isolate image processing (OpenCV) from the main process where practical.
- Storage: private buckets/keys; signed URLs for authorized access; never expose internal paths.

---

## 12. LLM SECURITY

- **Input control:** LLM receives only backend-constructed structured Route Profile — never raw client text/numbers as authoritative (`07_API_CONTRACT.md` §7.16, `02_TRD.md` §46–§47).
- **Grounding:** system instruction confines output to supplied data; no fabrication, no score modification, no safety guarantees (`02_TRD.md` §47).
- **Untrusted output:** validate/redact; render as plain text or sanitized markdown — never raw HTML (`08_UI_SPEC.md` §13); treat all LLM text as untrusted.
- **Prompt injection:** because input is structured-only and generated server-side, injection surface is minimized; if user questions are ever introduced, restrict and constrain them `[DECISION REQUIRED]`.
- **Keys:** LLM provider key via secrets manager; never in frontend/logs.
- **Fallback:** deterministic fallback on failure — structured data unaffected (`09_ERROR_HANDLING.md` §10.8).

---

## 13. EXTERNAL SERVICE SECURITY

Routing, facility, imagery, LLM providers are **untrusted dependencies**:
- All responses schema-validated at the adapter boundary (`02_TRD.md` §116).
- Provider credentials scoped per provider, rotated, never shared.
- TLS enforced on every provider call.
- Rate-limit/retry policy bounded; 4xx never retried (`09_ERROR_HANDLING.md` §11).
- Provenance recorded: `provider`, `provider_*_id`, `provider_timestamp` where exposed (`07_API_CONTRACT.md` §12).

---

## 14. DATABASE SECURITY

- Least-privilege roles: app role ≠ migration role ≠ admin.
- Parameterized queries/SQLAlchemy; no string-built SQL.
- TLS for client↔DB; encryption at rest.
- Backups: encrypted, tested restore; config backups exclude secrets (`02_TRD.md` §161).
- Migrations versioned (Alembic); destructive changes gated; see `runbooks/database-migration-failure.md`.
- No secrets stored as plaintext columns; tokens hashed if ever stored.

---

## 15. SECRETS MANAGEMENT

- **Never** in: source code, frontend bundle, git history, logs, error responses, screenshots, docs (except placeholders).
- Source: environment variables / OS secrets manager; `.env` local-only and gitignored; `.env.example` committed with placeholders.
- Rotation: scheduled + immediate on suspected leak (`runbooks/credential-reevocation-or-leak.md`).
- CI/CD secrets: injected as masked secrets; never echoed; scope to needed jobs.
- Key inventory: document which key belongs to which service and its rotation owner `[DECISION REQUIRED]`.

---

## 16. LOGGING, MONITORING & INCIDENT RESPONSE

- **Logging:** structured; fields `request_id, route_id, stage, duration_ms, error_code, status, provider, model_version`; never secrets/tokens/DB dumps (`09_ERROR_HANDLING.md` §12).
- **Monitoring/alerting metrics** per `02_TRD.md` §159; security signals: repeated auth failures (when auth exists), excessive requests, oversized payloads, provider anomalies, suspicious upload patterns (`02_TRD.md` §160).
- **Incident response:** follow `runbooks/` (credential leak, DB migration failure); document every incident + post-mortem in `16_CHANGELOG.md`; severity per `09_ERROR_HANDLING.md` §6.

---

## 17. INFRASTRUCTURE & CI/CD SECURITY

- Containers: non-root user, minimal base image, no baked-in secrets, image scanning.
- Builds: from pinned/locked deps; artifact checksum; reproducible builds.
- CI secret hygiene: masked env vars, no debug echo.
- Deployments: declarative config; production secrets via manager; no direct prod DB admin from laptops.
- Health/readiness endpoints don't leak internals (`07_API_CONTRACT.md` §7.17).

---

## 18. DEPENDENCY SECURITY

- Lockfiles committed (python/requirements lock or equivalent, `package-lock.json`).
- CVE scanning in CI (and deploy gate).
- Pin versions; prefer maintained, official, small packages (`MASTER_RULES.md` §30).
- No dependency added without justification; audit for supply-chain risk.

---

## 19. FRONTEND & UI SECURITY

- Encode/sanitize all dynamic text (esp. facility names, LLM output, provider data) — prevent XSS.
- CSP header; no unsafe-inline where avoidable.
- Never embed API keys/backend secrets in the bundle; frontend calls public `/api/v1` only (`02_TRD.md` §7).
- URL state: no sensitive data in URLs (`08_UI_SPEC.md` §19).
- Error boundary shows safe generic errors (no stack traces).

---

## 20. AI CODING-AGENT SECURITY RULES

When working on SafeRoute AI, the AI agent MUST:

1. Never commit, log, or output real secrets.
2. Keep `.env` gitignored; only commit `.env.example` placeholders.
3. Follow `MASTER_RULES.md` and this spec; no silent architecture changes.
4. Validate and sanitize all inputs; never trust client/external/LLM data.
5. Never render LLM/external text as HTML; encode output.
6. Keep ML artifacts versioned and checksummed; never silently swap models.
7. Never add dependencies without justification and review.
8. Handle failures per `09_ERROR_HANDLING.md` (no fabricated data; no unavailable→zero).
9. Search the repository for existing security controls before changing them.
10. Report any discovered secret/leak immediately and follow `runbooks/credential-reevocation-or-leak.md`.

---

## 21. SECURITY TESTING (with `14_TESTING`/`13_TESTING`)

- Input validation tests, injection attempts, malformed JSON, bad coordinates/enums, oversized/reused payloads.
- Upload tests: wrong MIME, fake extension, oversized, corrupt image → rejected.
- LLM: grounded-output tests, fallback on failure, untrusted text handling, prompt-injection attempts.
- Provider adapter: schema-validation tests, malformed provider responses.
- Frontend: XSS with malicious facility/route/LLM strings; CSP; no secret exposure in bundle.
- Dependency: CVE scan in CI; lockfile consistency.
- Secret scanning in CI/pre-commit (`git filter-repo` guidance in runbook for leaks).

---

## 22. RELATED DOCUMENTS

- `MASTER_RULES.md` §21 (security rules), §23 (no fabrication), §32 (logging)
- `02_TRD.md` §72–§77, §116–§117, §160
- `07_API_CONTRACT.md` §8 (authz), §13 (API security)
- `09_ERROR_HANDLING.md` (fail-closed, error sanitization)
- `04_DATA_MODEL.md` (status enums, model versioning)
- `05_DATA_SOURCES.md`, `06_SCRAPING_SPEC.md` (provider/collection trust)
- `runbooks/credential-reevocation-or-leak.md`
- `runbooks/database-migration-failure.md`

---

# END OF SECURITY SPECIFICATION