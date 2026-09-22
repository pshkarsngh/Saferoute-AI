# 18_ADMOB_SPEC.md — AdMob Specification (canonical)

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Authoritative AdMob (Monetization) Specification
**Version:** 1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_RULES.md` > `01_PRD.md` > this document
**Supersedes:** `11_ADMOB_SPEC.md` (now a pointer to this document)
**Related:** `10_SECURITY.md` (privacy), `08_UI_SPEC.md` (layout), `13_TESTING.md` (tests)

This is the single canonical source for all advertising behavior in SafeRoute AI.

---

## 1. PURPOSE

SafeRoute AI may monetize through Google AdMob display ads to sustain hosting and data costs. Advertising MUST NEVER change what the product computes or recommends. The analytical pipeline — routing, road imagery, OpenCV, YOLO11, hazard aggregation, risk scoring, facility discovery, and LLM explanation — is pure and unaffected by any ad state or impression (`MASTER_RULES.md` §4 project boundary).

---

## 2. MONETIZATION PRINCIPLE

- Ads are **presentation-layer decoration only**.
- The same source + destination produces the **same route analysis** regardless of advertiser, ad impression, fill rate, or monetization config.
- No ad unit, SDK callback, or monetization setting influences: route generation, route selection, hazard detection, risk score, facility counts, facility ordering, LLM prompt or model selection.
- **No sponsored content may be labeled or positioned as route, safety, hazard, or facility data.**

---

## 3. INDEPENDENCE FROM THE ANALYTICAL PIPELINE

| Analytical component | Ad interaction |
|----------------------|----------------|
| Routing (OSRM) | none |
| Road image collection | none |
| OpenCV preprocessing | none |
| YOLO11 detection | none |
| Hazard aggregation | none |
| Risk engine | none |
| Facility engine | none |
| LLM explanation | none |

- Ad code may touch only UI ad slots (banner/native containers).
- Ad-network failure, consent refusal, or no-fill MUST NOT degrade analysis in any way.

---

## 4. PLACEMENTS

| Placement | Format | Frequency / rule |
|-----------|--------|------------------|
| Route detail page | Banner (adaptive) | Below analytical content, above footer — never between/over risk or hazard data |
| End of route list | Native (low-frequency) | Max 1 per list page; never positioned so it suggests route ranking |
| Empty / loading / error states | None | No ads in empty, load, or error states |

**Prohibited**

- **No interstitial ad on app launch or during navigation** (high annoyance; previous spec rule preserved).
- No rewarded ads and no ad-gated features (analytics must never require watching ads).
- No ad covering hazard markers, emergency facilities, route controls, or map controls.

---

## 5. RULES

1. **Clear labeling** — ads visibly labeled "Ad"/"Sponsored"; nothing that impersonates organic content.
2. **No covering** — banners/natives never overlap hazard markers, emergency-facility markers, route selection, or map controls.
3. **Config-controlled unit IDs** — AdMob unit IDs come from configuration (`.env` / remote config), never hard-coded per environment.
4. **Test vs release IDs** — Google test unit IDs in dev/staging; **real unit IDs only in release builds**; never a test/release mix.
5. **Consent respected** — user consent/ads-disabled settings honored (`10_SECURITY.md`).
6. **Content-policy conflict** — no ad placed beside "official safety" claims or medical-looking text that could mislead users.

---

## 6. FAILURE HANDLING

- Ad load/show failures are **silent**: hide the slot without leaving blank space; never block content; never delay analysis rendering.
- SDK init failure → the app remains fully functional; ads just do not show.
- No retry loops that hammer the network (`05_DATA_SOURCES.md` provider-politeness spirit).
- Ad errors never leak stack traces, device identifiers, or analytics data into logs.

Failure modes: `no_fill`/`error`/`timeout`/`sdk_failed` are all treated as "hide slot, continue".

---

## 7. METRICS

Track only real, measured values (`MASTER_RULES.md` §23):

- Fill rate
- eCPM
- Block rate
- Ad load latency (time to first ad)
- Placement-level performance (drop underperforming/annoying placements)

Metrics inform placement decisions only; they NEVER feed or alter analytical results.

---

## 8. COMPLIANCE

- A clear privacy policy covering ad SDKs, data collection, and third-party sharing (`10_SECURITY.md`).
- Google Play policy compliance for ads and data collection.
- AdMob account compliance (certifications, disclosures, restricted-content review).
- Required ad-account declarations (e.g. app-ads.txt/TAG) completed as applicable.

---

## 9. RELATED DOCUMENTS

- `11_ADMOB_SPEC.md` (pointer to this canonical spec)
- `10_SECURITY.md` (privacy policy, ad SDK disclosure)
- `08_UI_SPEC.md` (layout slots hosting ads; no-cover rules)
- `13_TESTING.md` (ad-failure and no-influence tests)
- `MASTER_RULES.md` §4 (out-of-scope guard: ads must not change product behavior)

---

# END OF ADMOB SPECIFICATION