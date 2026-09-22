# Data Sources

## Source Policy

- Primary sources are official government portals only
- Every listing must carry an `official_url` back to the source
- No scraped data is presented as authoritative; the official link is always shown

## Candidate Sources

| Source | Type | Notes |
|--------|------|-------|
| Exam result portals | Results | e.g. official commission/board portals |
| Admit card portals | Admit cards | hall-ticket download pages |
| Employment/notification sites | Notifications | vacancy and application opens |

## Ingestion Rules

- Respect robots.txt and rate limits
- Add jitter and delays between requests
- Re-scrape on a schedule; use content `hash` to detect changes only
- De-duplicate by slug + source

## Storage

- Raw scraped content normalized into the `posts` table (see `04_DATA_MODEL.md`)