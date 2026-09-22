# Testing

## Strategy

- Test the behavior that matters: data ingestion correctness, API contracts, and feed/notification behavior in the app
- Prefer fast unit tests + a few integration tests over brittle end-to-end suites

## Coverage Areas

### Backend / API
- Endpoint contract tests (fields, status codes, error shapes from `07_API_CONTRACT.md`)
- Feed sort/cursor pagination
- Search and category filters
- Validation and error handling (`09_ERROR_HANDLING.md`)

### Scraping
- Parser tests against stored fixtures per source
- Change detection (hash diff) tests
- Idempotency: rerunning a scrape produces no duplicates

### Mobile App
- Feed rendering states: loading / error / empty / offline cache
- Bookmark add/remove and persistence
- Deep-link from notification → detail
- Search & filter flow

### Notifications
- Update on saved item triggers push payload
- Failure cleanup behavior

## Conventions

- Locked dependencies; deterministic test runs
- No tests that depend on live sources or network — use fixtures/mocks
- Run in CI on every push (`12_GITHUB_ACTIONS.md`)