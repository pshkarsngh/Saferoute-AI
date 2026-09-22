# GitHub Actions

## Workflows

### CI (on push / PR)

1. **Install** — restore dependencies (locked)
2. **Lint** — project linter
3. **Type-check / build** — verify code compiles/builds
4. **Unit tests** — run the test suite
5. **Security scan** — dependency vulnerability check
6. **Scraper contract check** — validate parsers against fixtures

### Deploy Backend (on merge to main)

1. Run CI steps above
2. Run migrations (see `database-migration-failure.md` runbook if they fail)
3. Deploy API service
4. Health check after deploy; rollback on failure

### Scrape (scheduled)

- Cron-triggered run of the scraper pipeline
- Emits metrics and alerts on failure thresholds

## Conventions

- Pin action versions by commit SHA where possible
- Secrets stored as GitHub secrets, never in the workflow file
- Approval gate for production deploys (if configured)
- Only run jobs relevant to changed code when feasible