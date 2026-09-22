# Decisions

Architecture and product decisions, logged with rationale. Latest first.

## ADR-005 — Push notifications for saved items via device tokens (v1)

- **Status:** Accepted
- **Context:** Users want alerts when a saved result/admit card updates, without building accounts.
- **Decision:** Client sends a device token; backend maps token → saved post ids and pushes on content change.
- **Consequences:** Push only for bookmarked items; tokens are sensitive data (see `10_SECURITY.md`); cleanup on delivery failure.

## ADR-004 — Bookmarks stored locally, no accounts in v1

- **Status:** Accepted
- **Context:** No auth/persistence infra desired for v1; offline support valued.
- **Decision:** Saved items live in local device storage.
- **Consequences:** No cross-device sync; simple and privacy-friendly.

## ADR-003 — API-driven scraping separated from serving

- **Status:** Accepted
- **Context:** Source sites can be slow or unavailable; serving must not block on ingestion.
- **Decision:** A scheduled scraper writes to the DB; the API reads only.
- **Consequences:** Clean separation; caching-friendly API; alerting on scraper health.

## ADR-002 — Content-hash change detection

- **Status:** Accepted
- **Context:** Need to detect updates without storing full history per source.
- **Decision:** Store a content hash per post; diff on each scrape; bump `updated_at` on change.
- **Consequences:** Cheap updates; drives notification triggers.

## ADR-001 — One parser per data source

- **Status:** Accepted
- **Context:** Sources differ in markup; a generic parser is brittle.
- **Decision:** A dedicated parser per `source_id`, returning a normalized JSON model.
- **Consequences:** New sources are additive; parser failures are isolated per source.