# Error Handling

## Principles

- Fail gracefully, never crash the app or pipeline silently
- User-facing messages are human-readable; technical details stay in logs
- Every failure path has a defined behavior and (where possible) a retry

## API Error Catalog

| Code | HTTP | Meaning | Client behavior |
|------|------|---------|-----------------|
| POST_NOT_FOUND | 404 | Post id unknown | Show empty/detail-missing state with retry |
| VALIDATION_ERROR | 400 | Bad query params | Fix request; hide error from user |
| RATE_LIMITED | 429 | Too many requests | Backoff + retry |
| UPSTREAM_UNAVAILABLE | 503 | Backend/data source down | Cache + retry; show offline banner |
| INTERNAL_ERROR | 500 | Unexpected | Retry then show generic error |

## Client Handling

- List/reload failures → non-blocking retry with snackbar
- Detail fetch failure → inline error state with **Retry**
- Offline (no network) → serve cached feed; banner "Offline — showing cached data"

## Scraper Handling

- Non-2xx or timeout: exponential backoff, max 3 attempts
- Parser exception: skip source this cycle, log + alert
- Persistent source failure (>N cycles): alert; surface in health metrics

## Notifications

- Delivery failures are logged; subscription cleaned up on repeat failure

## Logging / Alerting

- Structured logs: `{ts, level, service, event, detail}`
- Alerts on: scraper failure thresholds, 5xx rate, notification delivery drop