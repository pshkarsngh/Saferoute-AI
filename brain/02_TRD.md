# Technical Requirements Document (TRD)

## Overview

Implementation-level requirements that translate the PRD into buildable technical specifications.

## Platform

- Cross-platform mobile app (Android primary) using a single codebase
- Backend API serving scraped/curated exam data

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | Feed returns latest results, admit cards, notifications sorted by publish date |
| FR-02 | Search matches posts by title, category, and keyword |
| FR-03 | Filter by category (results / admit cards / notifications) |
| FR-04 | Detail page renders full post content and official links |
| FR-05 | Bookmarks persist locally per device |
| FR-06 | Push notifications sent on updates to saved items |

## Non-Functional Requirements

- Feed render under budget on low-end Android devices
- API responses served with caching headers
- Graceful offline state for bookmarks
- Sensitive keys never stored in the app

## Constraints

- Scraped data must link back to official government sources
- Rate limits and politeness required when scraping