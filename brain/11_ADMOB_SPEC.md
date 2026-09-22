# AdMob Specification

## Goal

Monetize via Google AdMob display ads without degrading the user experience.

## Ad Placements

| Placement | Format | Notes |
|-----------|--------|-------|
| Feed footer | Native or banner | No ad between every card; max 1 ad per page of feed |
| Detail page | Banner | Below content, above footer actions |
| Search results (empty/end) | Native | Low-frequency |

## Rules

- **No interstitial on launch or navigation** (high annoyance, hurts retention)
- Ads must be clearly labeled; nothing that impersonates organic content
- Respect content policy — do not place ads near misleading "official" claims
- Ad labels/unit IDs controlled via config, not hard-coded per environment

## Implementation

- Use the AdMob SDK through the app's official plugin/package
- Initialize once at app start; load ads lazily to keep first paint fast
- Handle failures silently (no blank space); never block content on ad load
- Test with test unit IDs in dev/staging; real IDs only in release builds

## Metrics

- Fill rate, eCPM, block rate, and ad-related latency
- Review placement performance; remove underperforming/annoying placements

## Compliance

- Clear privacy policy (see `10_SECURITY.md`) covering ad SDKs
- Comply with Google Play policy on ads and data collection