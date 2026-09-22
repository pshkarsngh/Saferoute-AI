# 11_ADMOB_SPEC.md — AdMob Specification

**Authoritative specification:** `18_ADMOB_SPEC.md`

The canonical SafeRoute AI monetization spec is **`brain/18_ADMOB_SPEC.md`**; this old slot is deprecated.

## Summary
- Ads are presentation-layer only; never alter routing, imagery, OpenCV, YOLO11, hazards, risk, facilities, or LLM.
- Banner below route-detail content; low-frequency native; NO interstitial on launch/navigation.
- Clearly labeled "Ad"; never cover hazards, emergency facilities, or route controls; config-controlled unit IDs; test IDs in dev/staging, real IDs only in release.
- Ads fail silently (no blank space); never block content.

## Related
- `18_ADMOB_SPEC.md` (authoritative) · `10_SECURITY.md` (privacy)