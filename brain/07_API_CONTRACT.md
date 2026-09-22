# API Contract

Base URL: `https://api.quicksarkariresults.example/v1`

## Authentication

- Public endpoints do not require auth in v1
- Admin/ingest endpoints require an API key in `Authorization: Bearer <key>`

## Endpoints

### GET /posts

Returns the feed or filtered list.

Query params:
- `category` — `results` | `admit_cards` | `notifications`
- `q` — search keyword
- `cursor` — pagination cursor
- `limit` — default 20, max 100

Response:
```json
{
  "items": [
    {
      "id": "uuid",
      "category": "results",
      "title": "…",
      "summary": "…",
      "official_url": "…",
      "publish_date": "2026-09-22T10:00:00Z",
      "updated_at": "2026-09-22T12:00:00Z"
    }
  ],
  "next_cursor": "…"
}
```

### GET /posts/{id}

Returns full detail:
```json
{
  "id": "uuid",
  "category": "results",
  "title": "…",
  "summary": "…",
  "content": "…",
  "official_url": "…",
  "publish_date": "2026-09-22T10:00:00Z",
  "updated_at": "2026-09-22T12:00:00Z"
}
```

### POST /subscribe {device_token} → push subscription for saved-item updates

Not a user account; push only for saved items.

## Errors

All errors return RFC 7807-ish shape:
```json
{ "error": { "code": "POST_NOT_FOUND", "message": "…" } }
```
See `09_ERROR_HANDLING.md` for the error catalog.

## Caching

- Feed/detail responses cacheable (`ETag`, `Cache-Control`)
- Client stores latest feed for offline rendering