# 12_GITHUB_ACTIONS.md — CI/CD (GitHub Actions)

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Authoritative CI/CD Workflow Specification
**Version:** 1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_RULES.md` > `01_PRD.md` > `02_TRD.md` > `03_ARCHITECTURE.md` > this document
**Related:** `15_DEPLOYMENT.md` (deploy mechanics), `runbooks/database-migration-failure.md` (migration incidents), `06_AI_SOURCES.md` + `09_ML_SPEC.md` (ML evaluation), `10_SECURITY.md` (secret management)

A green pipeline means only that the listed checks ran and passed — never a substitute for real evidence (`MASTER_RULES.md` §23).

---

## 1. PURPOSE

- Code is linted, type-checked, built, and unit-tested on every push/PR.
- Security (CVE) and secret scans run in CI.
- Backend deploys are repeatable, verifiable, and reversible.
- ML model evaluation can run on a schedule.
- Secrets never appear in workflow files or artifacts.

---

## 2. WORKFLOWS

### 2.1 CI (on push / pull_request)

Triggers: `push` to main + all `pull_request`.

Steps (any failure fails the job):

1. **Install locked dependencies** — Python from tracked lockfile (`requirements.txt`/`uv.lock`); Node via `npm ci` / `pnpm install --frozen-lockfile`. Lockfiles are committed (`10_SECURITY.md`).
2. **Lint** — `ruff check .` (backend), `eslint` (frontend).
3. **Type-check / build** — `mypy app` (backend); `tsc --noEmit` + `npm run build` (frontend).
4. **Unit tests** — `pytest -q` (backend), Vitest + React Testing Library (frontend) (`13_TESTING.md`).
5. **Security / CVE scan** — dependency vulnerability scan on the locked graph (e.g. `pip-audit`, `npm audit` / OSV).
6. **Secret scan** — scan the diff for leaked secrets/keys (e.g. gitleaks); any hit fails the job; values are never printed.

Optional jobs:

- **ML smoke** — validate `ml/dataset/data.yaml` consistency (classes match config), confirm no model artifacts staged.
- **Integration smoke** — against a temporary PostgreSQL 16 container when it adds value.

### 2.2 Deploy Backend (on merge to main)

Triggers: `push` to `main` (or a tagged `workflow_dispatch`). Production deploys require the approval gate (§3).

Sequence:

1. **CI** — run the §2.1 job set to completion; deploy never bypasses CI.
2. **Migrations** — run Alembic migrations against the target DB. **On failure:** halt the deploy and follow `runbooks/database-migration-failure.md` immediately (halt further deploys, assess, fix-forward or rollback). Never auto-deploy over a failed migration.
3. **Deploy** — rollout the backend release (mechanics per `15_DEPLOYMENT.md`).
4. **Health check** — poll `GET /api/v1/health` plus a smoke request; proceed only when healthy.
5. **Rollback on failure** — if health/smoke fails within the watch window, automatically roll back to the previous release (previous image + consistent migration state per the runbook), re-check health, and alert.

All secrets used in deploy steps come from GitHub Secrets / platform secrets — never from the repo or workflow body.

### 2.3 Scheduled ML Evaluation (optional)

Triggers: cron (nightly/weekly) + `workflow_dispatch`.

Purpose (`06_AI_SOURCES.md` §10, `09_ML_SPEC.md` §13):

1. Load the registered model version and run it over the held-out test subset.
2. Record precision/recall/mAP/F1 per class — measured values only, no fabricated metrics (`MASTER_RULES.md` §23).
3. Store metrics as checksummed artifacts and post a summary.
4. Alert only on verified thresholds (e.g. recall drop). This job NEVER deploys anything.

---

## 3. CONVENTIONS

- **Pin action versions** — third-party actions pinned by commit SHA (or at minimum a fixed `@vN`); never a floating `@main`.
- **Secrets** — all secrets are GitHub Secrets / secret-manager values via `${{ secrets.X }}`; no literals, no values in logs, no secrets in artifacts or caches.
- **Approval gate for prod** — production deploys require an explicit environment approval; staging/preview may be automatic.
- **Run only relevant jobs** — path filters run frontend/backend/ML jobs only when the corresponding paths changed; required security jobs are never skipped.
- **Artifact checksums** — build and migration artifacts are sha256-checksummed; manifests record artifact → checksum so deploys are reproducible and verifiable (`06_AI_SOURCES.md` §7).
- **Cache hygiene** — dependency caches keyed by lockfile hash; env/encrypted data never cached.
- **No ambient credentials** — workflows never assume local `.env`; credentials are injected per job.

---

## 4. FAILURE RULES

- Red CI blocks merge and deploy.
- Migration failure → follow `runbooks/database-migration-failure.md`; deploy halts until resolved.
- Health-check failure → rollback (never "wait and watch silently").
- Any accidentally exposed secret → incident per `runbooks/credential-reevocation-or-leak.md`.

---

## 5. RELATED DOCUMENTS

- `15_DEPLOYMENT.md` (deployment mechanics, environment separation, rollback procedure)
- `runbooks/database-migration-failure.md` (migration incident procedure)
- `runbooks/credential-reevocation-or-leak.md` (secret-exposure incident)
- `13_TESTING.md` (the tests run in CI)
- `10_SECURITY.md` (dependency scan, secret management)
- `06_AI_SOURCES.md`, `09_ML_SPEC.md` (ML evaluation job)

---

# END OF CI/CD SPECIFICATION