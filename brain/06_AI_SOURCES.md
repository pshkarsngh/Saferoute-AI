# 06_AI_SOURCES.md — AI/ML Data & Model Sources Specification

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Authoritative AI/ML Data & Model Sources Specification
**Version:** 1.0
**Status:** Implementation-Ready
**Authority:** `MASTER_RULES.md` > `01_PRD.md` > `02_TRD.md` > `03_ARCHITECTURE.md` > `04_DATA_MODEL.md` > `05_DATA_SOURCES.md` > this document
**Companion:** `09_ML_SPEC.md` (pipeline behavior), `06_SCRAPING_SPEC.md` (permitted collection), `10_SECURITY.md` (artifact integrity), `02_TRD.md` §21–§25, §54–§55

---

## 1. PURPOSE

SafeRoute AI detects road hazards with a trained YOLO11 model (`MASTER_RULES.md` §8). A model is only as trustworthy as the dataset it was trained on and the versioning that links a production detection back to a specific dataset + model version (`MASTER_RULES.md` §25).

This document specifies:

- Dataset requirements and layout under `ml/dataset`.
- Dataset documentation requirements — what must be recorded, and what must never be invented.
- Imagery licensing rules for ML use.
- Model artifact storage (gitignored, checksummed, versioned).
- The model lifecycle: **train → validate → export → register → serve**.
- Evaluation metrics and their meaning (precision / recall / mAP / F1 / per-class).
- Train/test leakage controls.
- Traceability through the `ModelVersion` and `DatasetVersion` entities (`04_DATA_MODEL.md` §7.13–§7.14).

Non-negotiable: **no fabricated dataset statistics, no fabricated model metrics, no invented classes** (`MASTER_RULES.md` §23, §35).

---

## 2. DOCUMENT AUTHORITY

- Every statement here extends `05_DATA_SOURCES.md` §4 (YOLO11 Dataset & Model). Where the two conflict, the higher-authority document wins and the conflict is recorded.
- Dataset numbers (counts, split ratios, metrics) MUST come from measured artifacts, never from guesswork.
- This document does not invent new ML products; it defines data/model source requirements for the hazard-detection scope approved in `01_PRD.md` and `02_TRD.md`.

---

## 3. SCOPE

In scope:

- The YOLO11 hazard-detection dataset (images + labels) used for training/validation/testing.
- Model artifacts produced from that dataset.
- Versioning, checksums, storage, and lifecycle governance.
- Evaluation and leakage controls.

Out of scope (unless explicitly approved, `MASTER_RULES.md` §4):

- Additional vision models (segmentation, depth, driver monitoring).
- Real-time video detection inside a moving vehicle.
- Crowd-sourced personal image collection.

---

## 4. DATASET REQUIREMENTS (ml/dataset)

Training data MUST be separated from production code (`MASTER_RULES.md` §9). Canonical layout:

```
ml/
├── dataset/
│   ├── images/
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   ├── labels/
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   └── data.yaml
├── training/            # training scripts + config, committed
└── models/              # artifacts — GITIGNORED (never committed)
```

### 4.1 Images

- Every image is a single valid raster file (commonly JPEG/PNG) that matches exactly one label file of the same basename.
- Images are original frames or crops derived from permitted imagery — never screenshots of third-party products without a license.
- The final model input size is a preprocessing decision (`09_ML_SPEC.md` §5); on-disk images may be larger, and OpenCV applies the documented fixed input size before inference.

### 4.2 Labels

- YOLO-format text files (`class_id cx cy w h`, normalized 0..1) — one per image, basename-matched.
- `class_id` MUST equal the index of the class name in `data.yaml`.
- Label files are annotation truth, not model output. Annotations must reflect the documented annotation methodology (§6.5 requirement).

### 4.3 data.yaml

`data.yaml` is the authoritative class definition (`MASTER_RULES.md` §8) and split pointer:

```yaml
# EXAMPLE STRUCTURE — all values illustrative
path: ../dataset
train: images/train
val: images/val
test: images/test
names:
  0: pothole
  1: road_crack
  2: damaged_road
  3: obstacle
  4: debris
```

- The `names` list is the class list used at inference time. Application classes, model classes, and `data.yaml` classes MUST stay consistent (`02_TRD.md` §23).
- Only classes actually present in the annotated dataset may be listed. Never invent classes.
- `data.yaml` may live in the repo; images, labels, and model artifacts do not (`MASTER_RULES.md` §9).

### 4.4 Split requirement

- Images and labels are split into `train/`, `val/`, and `test/` (never train/val alone).
- `test/` is held out. It is never used for training decisions (metric selection, early stopping, augmentation tuning).
- The split is performed once by a deterministic, documented splitter, and the result is recorded in the dataset documentation (§5).

---

## 5. DATASET DOCUMENTATION REQUIREMENTS

Every released dataset version MUST ship a documentation entry (see `docs/AI_MODELS.md` per `05_DATA_SOURCES.md` §4) recording:

| # | Field | Requirement |
|---|-------|-------------|
| 1 | source | Where the imagery came from (provider or project ownership) |
| 2 | license | License/terms that permit training + inference use |
| 3 | classes | Class list + class_id mapping (must match `data.yaml`) |
| 4 | annotation methodology | Who/how annotated; tooling; label convention; QA step |
| 5 | split methodology | Deterministic splitter, seed, ratios, hold-out test |
| 6 | preprocessing | Image transforms applied before saving |
| 7 | augmentation | Offline/online augmentation applied, and when |
| 8 | version | Dataset name + version (e.g. `road-hazards-v1`) |
| 9 | limitations | Geographic scope, weather, lighting, camera, temporal age |

Rules:

- Every documented value MUST be a measured fact. **Never fabricate dataset statistics** (`MASTER_RULES.md` §23; `04_DATA_MODEL.md` §7.14 note).
- Unmeasured quantities (e.g. exact per-class distribution) are measured or omitted — never guessed.
- Augmentation is versioned per preprocessing pipeline so cache keys remain valid (`MASTER_RULES.md` §33).

---

## 6. IMAGERY LICENSING FOR ML

Every image in `ml/dataset` MUST be permitted for the intended use:

1. **Project-owned imagery** — captured by the project; document device, area, capture date.
2. **Licensed imagery** — the license explicitly permits ML training/validation; store license evidence with the dataset documentation.
3. **Permitted public imagery** — only where terms permit copying and derivative use for ML (e.g. compatible CC/ODbL-style terms), verified per source (`06_SCRAPING_SPEC.md`).

Forbidden:

- Imagery whose terms prohibit derivative ML use.
- Crawled/scraped imagery without explicit permission.
- Uncredited imagery from unspecified sources.
- Imagery that exposes personal/identifying information beyond incidental street content (`06_SCRAPING_SPEC.md`).

`[DECISION REQUIRED]` — Street-level imagery provider for ML is NOT finalized:

- What is missing: which licensed provider (or project-owned capture) supplies the dataset imagery.
- Why it matters: dataset `source`/`license` fields and `RoadImage.source` depend on it.
- Options: project-owned capture; a licensed street-level provider; a public-domain image database.
- Affected documents: `05_DATA_SOURCES.md` §2, this document §5–§6, `04_DATA_MODEL.md` §7.6.

`[DECISION REQUIRED]` — Dataset-building collection path is NOT finalized:

- What is missing: explicit confirmation that no dataset imagery will be harvested from third-party mapping products.
- Why it matters: ToS/license risk; affects the dataset documentation `source`/`license` fields.
- Options: restrict all dataset imagery to project-owned or explicitly licensed feeds.
- Affected documents: `06_SCRAPING_SPEC.md`, this document §6.

---

## 7. MODEL ARTIFACT STORAGE

- Artifacts live in `ml/models/`, which is **gitignored** (`03_ARCHITECTURE.md` §3; `MASTER_RULES.md` §9).
- The repository contains only configuration, training scripts, and documentation — never `.pt`/`.onnx` weights.
- Storage requirements:

| Property | Requirement |
|----------|-------------|
| Location | `ml/models/<model-name>-v<version>.(pt | onnx)` or object storage |
| Git | never committed |
| Checksum | sha256 recorded in `ModelVersion.checksum` (`04_DATA_MODEL.md` §7.13) |
| Version | unique `model_name` + `model_version` |
| Path config | `MODEL_PATH` env/config — never hard-coded (`MASTER_RULES.md` §24) |

- Checksums are verified at load time (`10_SECURITY.md`; `09_ML_SPEC.md` §9).
- Artifact retention follows the model lifecycle: retired models are archived, not silently deleted, while historical detections still reference them.

---

## 8. MODEL LIFECYCLE

```
TRAIN  →  VALIDATE  →  EXPORT  →  REGISTER  →  SERVE
  │            │           │          │            │
dataset      metrics     .pt/onnx   ModelVersion  inference via
version      on test     + sha256    record       MODEL_PATH
```

1. **Train** — `ml/training/train.py` with committed config; dataset version pinned in the training config.
2. **Validate** — evaluate on the held-out test set; record metrics (§10). Training completing is NOT evidence of sufficiency (`02_TRD.md` §54).
3. **Export** — export to the deployable format (`.pt` and/or `.onnx`); compute the sha256 checksum.
4. **Register** — create `ModelVersion` linked to `DatasetVersion`; exactly one model is `active` at a time (`04_DATA_MODEL.md` §7.13).
5. **Serve** — controlled switch of `MODEL_PATH`/`MODEL_VERSION`; model-version-dependent cache keys are invalidated (`MASTER_RULES.md` §33).

Rules:

- **Never silently replace the trained model** (`MASTER_RULES.md` §8, §25).
- A new version requires a new `ModelVersion` row, a new checksum, and a documented change note.
- Production inference only uses a model that is **registered + active** and passed the deployable checks (§7).

---

## 9. NO TRAIN/TEST LEAKAGE

- `test/` images never appear in `train/` or `val/`, and never influence training decisions.
- Near-duplicate detection (image hashing, e.g. `road_images.image_hash`) SHOULD quarantine near-duplicate images across splits so held-out answers are not given away.
- Augmentation that changes label distribution is documented; test evaluation uses a fixed, non-augmented test set.
- The splitter's seed and version are recorded so leakage checks are reproducible.

---

## 10. EVALUATION METRICS

Reported for every model version, computed on the held-out `test` set — never fabricated (`02_TRD.md` §54; `MASTER_RULES.md` §23):

- **Precision** — of detections above threshold, the fraction correct.
- **Recall** — of true objects, the fraction detected.
- **mAP** — mean Average Precision across classes (report at the documented IoU setting).
- **F1** — harmonic mean at the operating threshold (or the F1 curve).
- **Per-class** — precision/recall per class, because rare classes dominate risk usefulness.
- **Confusion matrix** — stored with the evaluation run where practical.

Rules:

- Metrics are bound to `ModelVersion` + `DatasetVersion` + evaluation config (threshold, IoU, test split).
- Report operating-point metrics at the production `CONFIDENCE_THRESHOLD` and `YOLO_IOU_THRESHOLD` (`09_ML_SPEC.md` §5), not only optimal-curve points.
- Never claim a metric exists without the evaluation run; store the run artifact.
- **Definition of done for a model candidate:** validated metrics recorded, no leakage, artifact checksummed, version registered.

---

## 11. TRACEABILITY (ModelVersion / DatasetVersion)

Per `04_DATA_MODEL.md` §7.13–§7.14:

- `DatasetVersion` — dataset name/version, source, license, class count, `data.yaml` reference, measured split counts, preprocessing version.
- `ModelVersion` — model name/version, framework, artifact reference, `dataset_version_id`, thresholds, checksum, status, lifecycle timestamps; `UNIQUE(model_name, model_version)`.

Traceability invariants:

1. Every `HazardDetection.model_version_id` MUST resolve to a registered `ModelVersion` (`04_DATA_MODEL.md` §13; `02_TRD.md` §167).
2. Every `ModelVersion.dataset_version_id` MUST resolve to a `DatasetVersion`.
3. Detections without version provenance are rejected (`09_ERROR_HANDLING.md` §5).
4. Risk-score chain: `risk_score → RiskAnalysis → Hazard → HazardDetection → ModelVersion → DatasetVersion → images` (`04_DATA_MODEL.md` §7.16).

Cache keys MUST include model version and inference configuration (`MASTER_RULES.md` §33; `02_TRD.md` §85).

---

## 12. RELATIONSHIP TO DATA SOURCES & SCRAPING

- `05_DATA_SOURCES.md` §4 defines the YOLO11 dataset/model as a data source: location `ml/dataset`, only permitted/annotated imagery, classes from `data.yaml`, config via environment.
- `06_SCRAPING_SPEC.md` governs HOW collected imagery may be obtained: prefer provider APIs, scrape only where permitted, no ToS/legal bypass, no PII, source + timestamp capture, schema validation, idempotent runs.
- This document governs HOW the resulting dataset/model is documented, versioned, and stored.
- Routing (OSRM) and facility (Overpass) data never enter the ML dataset; they feed the route and facility domains only.

---

## 13. RELATED DOCUMENTS

- `MASTER_RULES.md` §7–§9, §23, §25 (OpenCV/YOLO split, dataset rules, no-fabrication, versioning)
- `02_TRD.md` §21–§25, §54–§55 (YOLO config, versioning, metrics, dataset management)
- `05_DATA_SOURCES.md` §4 (source-level facts)
- `06_SCRAPING_SPEC.md` (permitted collection policy)
- `09_ML_SPEC.md` (pipeline behavior, loading, failure modes)
- `04_DATA_MODEL.md` §7.13–§7.14, §13 (entities + traceability)
- `10_SECURITY.md` (artifact integrity, checksum verification)
- `09_ERROR_HANDLING.md` §5 (model/version failure handling)

---

# END OF AI/ML DATA & MODEL SOURCES SPECIFICATION