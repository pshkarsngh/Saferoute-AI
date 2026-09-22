# Data Model

## Entities

### Post (listing = result / admit card / notification)

| Field | Type | Notes |
|-------|------|-------|
| id | string (uuid) | primary key |
| category | enum | `results` \| `admit_cards` \| `notifications` |
| title | string | human-readable headline |
| slug | string | URL-safe identifier |
| summary | text | short description |
| content | text | full detail page content |
| official_url | string | link to official source |
| publish_date | datetime | feed sort key |
| updated_at | datetime | triggers change detection |
| source_id | string | originating source |
| hash | string | content hash for dedupe/change detection |

### SavedItem (client-side)

| Field | Type |
|-------|------|
| post_id | string |
| saved_at | datetime |

## Indexes

- `posts(category, publish_date)` — feed query
- `posts(title)` — search
- `posts(slug)` — unique

## Change Detection

- Content `hash` compared on each scrape; changes update `updated_at` and fire notifications for saved items.