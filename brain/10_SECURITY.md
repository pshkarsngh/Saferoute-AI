# 10_SECURITY.md — Security Requirements

**Authoritative specification:** `security_handling.md`

This slot is reserved in the numbered documentation series (per the project file map: `10_SECURITY.md` = Security requirements). The complete SafeRoute AI security specification lives in **`brain/security_handling.md`** and is authoritative.

## Summary of requirements

- Secrets never in code, git, frontend bundles, logs, or error responses; `.env` gitignored; `.env.example` placeholders only; secrets manager in deploy (`MASTER_RULES.md` §21).
- Input validation (typed schemas, coordinate/enum ranges), rate limiting, CORS policy, secure headers (CSP/HSTS), injection protection.
- Provider/LLM/uploaded data treated as untrusted; schema-validated at boundaries.
- LLM output is untrusted text — grounded, validated, never rendered as unsafe HTML, never authoritative.
- Model artifacts versioned + checksummed; detections traceable to `model_version` (integrity).
- Least privilege, defense in depth, zero trust between services; internal ML/admin endpoints never public.
- Structured logging with never-log list; monitoring + alerting; incident procedures in `runbooks/`.
- Dependency/SCA scanning in CI; lockfiles; minimal dependencies.
- AI coding agents follow §20 of `security_handling.md`.

## Related

- `security_handling.md` (authoritative full spec)
- `09_ERROR_HANDLING.md` (fail-closed + sanitization)
- `07_API_CONTRACT.md` §8/§13
- `runbooks/credential-reevocation-or-leak.md`
- `runbooks/database-migration-failure.md`