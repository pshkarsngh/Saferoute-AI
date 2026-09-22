# Production Checklist

Use before a production release and after deploy.

## Before Release

- [ ] All CI checks green (lint, build, tests, security scan)
- [ ] Migrations reviewed and tested on a production-like dataset
- [ ] Secrets configured in the secrets manager (never in repo)
- [ ] AdMob unit IDs swapped to production IDs
- [ ] Privacy policy current and linked in the store listing
- [ ] Changelog updated (`16_CHANGELOG.md`)
- [ ] Data source list reviewed; all `official_url`s valid
- [ ] Rollback plan defined (previous release artifact + step to revert)

## After Deploy

- [ ] Health checks pass; no 5xx spike
- [ ] Feed/detail loaded with expected latency
- [ ] Scraper run succeeded; fresh data visible
- [ ] Notifications deliver and deep-link correctly
- [ ] Ads fill without layout issues
- [ ] Monitoring/alerting configured and noise-free
- [ ] Incident runbooks accessible to the on-call team

## Monitoring

- API error rate, latency, throughput
- Scraper success/failure per source
- Notification delivery rate
- Ad fill rate / eCPM
- Crash-free sessions (mobile)