# Database Migration Failure

## Severity
High

## Overview
A database migration has failed, leaving the schema or data in an inconsistent state, or blocking a deployment.

## Detection
- CI/CD pipeline failure on migration step
- Application errors after deploy (missing table/column, type mismatch)
- Migration tool reports a failed or partially applied migration

## Response

### 1. Assess
- Identify which migration failed and at which step
- Check database state: which migrations are marked applied vs. actual schema
- Determine if the app is still running or down

### 2. Contain
- Halt further deployments that depend on this migration
- If the app is broken, consider rolling back to the previous release

### 3. Recover

**Option A — Fix forward (preferred for data migrations):**
- Write a corrective migration that fixes the broken state
- Run it in a staging environment first
- Apply to production during a safe window

**Option B — Rollback:**
- Revert the application to the previous version
- Roll back the migration if the tool supports it (e.g., `migrate down`, `alembic downgrade`)
- Verify schema matches the previous app version

### 4. Verify
- Confirm schema integrity (`\d`, migration status table, schema diff)
- Run application health checks and critical-path smoke tests
- Monitor error rates after recovery

## Post-Incident
- Root-cause the failure (bad SQL, lock timeout, dependency on live data, non-idempotent migration)
- Add migration dry-run/CI checks against a production-like dataset
- Ensure all migrations are reversible and tested in staging first
