# Security

## Secrets

- No secrets in code, config files, or the repo
- Store in a secrets manager; inject via environment variables
- Rotation on a schedule and immediately on suspected leak (see `runbooks/credential-reevocation-or-leak.md`)

## API

- Ingest/admin endpoints protected by API key (Bearer)
- Validate and sanitize all inputs; never trust client data
- Rate limiting on all endpoints

## Data

- All data is public; no user PII stored in v1 (no accounts)
- Push subscription tokens are the only user data; treat as sensitive, encrypt at rest

## Transport

- HTTPS everywhere; HSTS enabled
- No insecure downgrade paths

## Mobile App

- HTTPS-only network calls (ATS + Android network security config)
- Bookmarks stored locally; no sensitive data in transit
- Keep dependencies updated; scan for known CVEs in CI

## Dependencies

- Lock files committed (e.g. lockfile / package-lock.json / pubspec.lock)
- CI runs dependency security scan
- Same-origin/official packages only; pin versions

## Incident Handling

- Follow `runbooks` for credential leaks and migration failures
- Document every security incident in `16_CHANGELOG.md` / post-mortem