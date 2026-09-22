# Scraping Specification

## Goal

Keep the `posts` table fresh and accurate while respecting source owners.

## Pipeline

```
schedule → fetch page → parse/extract → normalize → hash → diff → upsert → notify
```

## Steps

1. **Fetch** — HTTP GET with polite UA, retries, and backoff
2. **Parse** — extract title, category, content, official_url, publish_date
3. **Normalize** — clean whitespace, unify date formats, strip junk
4. **Hash** — compute content hash
5. **Diff** — compare against stored hash
6. **Upsert** — insert new posts or update changed posts
7. **Notify** — if `updated_at` changes, trigger push to users who saved the post

## Parsers

- One parser per source site, selected by `source_id`
- Parsers return a JSON model of extracted fields (no HTML-aware client logic)

## Error Handling

- Non-2xx → retry with exponential backoff (max 3)
- Parser failure → log, alert, and skip source (never crash the pipeline)

## Schedule

- Source sites checked on a fixed interval (see config)
- Run is idempotent: rerunning produces no duplicates

## Health

- Emit scrape success/failure metrics per source
- Alert on sustained parser failures (see `09_ERROR_HANDLING.md`)