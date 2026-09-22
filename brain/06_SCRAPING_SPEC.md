# Scraping / Data Collection Specification — SafeRoute AI

Scope: any web-based collection of data (scraping) used in SafeRoute AI. SafeRoute AI is primarily API-driven; scraping is allowed **only** where permitted and where a provider API is unavailable or insufficient.

## Policy (read first)

1. **Prefer official provider APIs** (routing, facilities, imagery, LLM). Do not scrape what a provider API already offers.
2. **Scrape only where permitted**: respect `robots.txt`, terms of service, licensing, and `data.yaml`/dataset licensing for ML data.
3. **No bypassing**: no CAPTCHA bypass, no credential abuse, no rate-limit evasion, no legal or ToS violations.
4. **No PII collection**: never collect or store personal data.
5. **Confidence to source**: everything collected must keep its source + timestamp and pass through schema validation (`TRD` §116).
6. **Imagery for ML**: only annotated, licensed imagery may enter `ml/dataset`; document the source and license in `docs/AI_MODELS.md`.

## When Scraping Is Allowed

| Case | Allowed? | Notes |
|------|----------|-------|
| Fetch facility data | No | Use facility provider API (Overpass) |
| Fetch routing data | No | Use routing provider API (OSRM) |
| Road imagery (licensed, permitted source) | Yes | Logged with source; metadata required |
| Dataset building for YOLO training | Yes | Only licensed/own imagery; documented in `ml/dataset` |
| LLM outputs | No | Use LLM provider API |
| Any site that forbids it / requires auth to access | No | Respect ToS |

## Collection Pipeline (when used)

```
Permitted Source
   → Fetch (polite client, UA, timeout, retries)
   → Validate (robots/ToS/HTTP status)
   → Parse / Extract
   → Normalize to internal schema
   → Attach metadata (source, timestamp)
   → Validate schema (TRD §116)
   → Store / concommit with source traceability
```

## Politeness & Reliability

- Polite request pacing + jitter; never hammer a source.
- Per-request timeout and capped retries (transient only; `TRD` §97–§98).
- Respect 429/backoff; cache results (`TRD` §96).
- Idempotent runs — reruns never duplicate stored data.

## ML Dataset Rules

- `ml/dataset/images/{train,val,test}` + `ml/dataset/labels/{train,val,test}` + `data.yaml`.
- Every image must be licensed/own and documented; no fabricated statistics (`TRD` §154).
- Only dataset classes appear in production inference (`TRD` §23).
- Huge generated datasets and model artifacts are gitignored — never committed (`MASTER_RULES` §9).

## Failure Handling

- Non-2xx or parse failure → log, classify (e.g. `IMAGE_ERROR`), retry only transient, then skip source this cycle.
- Never fabricate missing data; mark `unavailable` (`TRD` §169).
- Collection failures feed observability metrics (`TRD` §159).

## Related Docs

- `05_DATA_SOURCES.md` (provider-first source strategy)
- `04_DATA_MODEL.md` (where collected data is stored)
- `02_TRD.md` §96–§98, §116, §154