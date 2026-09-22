# UI Specification

## Platform

Cross-platform mobile app (Android first, iOS later).

## Screens

### 1. Feed (Home)

- Tabs/filter chips: **Results · Admit Cards · Notifications**
- Cards show title, category badge, summary, publish date
- Pull-to-refresh; infinite scroll via cursor pagination
- Bookmark icon on each card

### 2. Search

- Top search bar
- Results grouped by category
- Filters: category chips + date sort

### 3. Detail

- Full title, content, badges
- Primary button: **Official Source** (opens `official_url`)
- Bookmark toggle

### 4. Saved

- List of bookmarked posts (local storage)
- Works offline; shows stale date badge

### 5. Settings

- Notifications on/off
- Default feed category
- About / privacy

## Design Notes

- Low-end-device friendly: small bundle, fast first paint
- Follow platform accessibility guidelines (touch targets, contrast, a11y labels)
- States: loading, error w/ retry, empty, offline

## Notifications

- Local notification tapped → deep link to post detail
- Permission requested in context (not on first launch)