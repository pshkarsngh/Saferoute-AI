# SAFEROUTE AI

# Technical Requirements Document (TRD)

**Project:** SafeRoute AI — Intelligent Road Safety Navigation System
**Document:** Technical Requirements Document
**Version:** 1.0
**Status:** Development
**Document Type:** System / Software / AI-ML Technical Specification
**Related Documents:**

* `MASTER_RULES.md`
* `PRD.md`
* `docs/ARCHITECTURE.md`
* `docs/AI_MODELS.md`
* `docs/DATABASE.md`
* `docs/API.md`
* `docs/RISK_ENGINE.md`

---

# 1. PURPOSE

This Technical Requirements Document defines the technical implementation requirements for SafeRoute AI.

The purpose of this document is to remove ambiguity from the implementation.

The AI coding agent and developers MUST use this document to determine:

* System architecture
* Component responsibilities
* Data flow
* API contracts
* Database structure
* ML pipeline
* YOLO11 integration
* OpenCV pipeline
* Route processing
* Hazard processing
* Risk calculation
* Facility processing
* LLM integration
* Frontend behavior
* Backend behavior
* Security
* Performance
* Testing
* Logging
* Configuration
* Error handling
* Deployment

---

# 2. DOCUMENT AUTHORITY

The project documentation hierarchy is:

```text
1. Explicit project-owner requirement
2. MASTER_RULES.md
3. PRD.md
4. TRD.md
5. Architecture documentation
6. Existing implementation
```

If two technical documents conflict:

1. Do not silently choose one.
2. Identify the conflict.
3. Preserve existing working functionality.
4. Request project-owner clarification when required.

---

# 3. SYSTEM OBJECTIVE

SafeRoute AI shall implement the following technical pipeline:

```text
USER
  |
  v
FRONTEND
  |
  v
BACKEND API
  |
  v
ROUTING PROVIDER
  |
  v
ROUTE NORMALIZATION
  |
  +-----------------------------+
  |                             |
  v                             v
ROAD IMAGE PIPELINE       ROUTE METADATA
  |
  v
OPENCV
  |
  v
YOLO11
  |
  v
HAZARD DETECTION
  |
  v
HAZARD AGGREGATION
  |
  v
RISK ENGINE
  |
  +-----------------------------+
  |                             |
  v                             v
FACILITY ENGINE           ROUTE PROFILE
  |                             |
  +--------------+--------------+
                 |
                 v
          LLM EXPLANATION
                 |
                 v
             FRONTEND
```

---

# 4. CORE ARCHITECTURAL PRINCIPLE

Each subsystem has a specific responsibility.

| Component            | Responsibility                           |
| -------------------- | ---------------------------------------- |
| Frontend             | User interaction and visualization       |
| Backend              | Validation and orchestration             |
| Routing Provider     | Candidate route generation               |
| Route Normalizer     | Convert provider data to internal format |
| Image Pipeline       | Collect and prepare road imagery         |
| OpenCV               | Image preprocessing                      |
| YOLO11               | Road-hazard detection                    |
| Hazard Engine        | Detection aggregation                    |
| Risk Engine          | Deterministic risk calculation           |
| Facility Engine      | Nearby facility discovery                |
| Route Profile Engine | Combine verified route information       |
| LLM                  | Natural-language explanation             |
| Database             | Persistent structured data               |
| Cache                | Reuse valid expensive results            |

No component should silently assume another component's responsibility.

---

# 5. SUPPORTED ROUTE MODEL

The system MUST support:

```text
1 route
2 routes
3 routes
4 routes
```

The system MUST NOT assume four routes are always available.

Maximum candidate routes:

```text
MAX_CANDIDATE_ROUTES = 4
```

The value should be configurable where practical.

---

# 6. HIGH-LEVEL COMPONENT ARCHITECTURE

Recommended logical backend structure:

```text
backend/
│
├── api/
│   ├── routes/
│   ├── analysis/
│   ├── facilities/
│   └── llm/
│
├── core/
│   ├── config/
│   ├── logging/
│   ├── security/
│   └── errors/
│
├── routing/
│   ├── provider/
│   ├── normalizer/
│   └── models/
│
├── vision/
│   ├── preprocessing/
│   ├── yolo/
│   └── models/
│
├── hazards/
│   ├── detection/
│   ├── aggregation/
│   └── models/
│
├── risk/
│   ├── calculator/
│   ├── weights/
│   └── models/
│
├── facilities/
│   ├── provider/
│   ├── search/
│   ├── aggregation/
│   └── models/
│
├── route_analysis/
│   ├── service/
│   └── models/
│
├── llm/
│   ├── prompts/
│   ├── service/
│   └── models/
│
├── database/
│   ├── models/
│   ├── repositories/
│   └── migrations/
│
└── tests/
```

The exact directory names may differ depending on the chosen framework.

The architecture MUST remain modular even if implemented as a modular monolith.

---

# 7. FRONTEND TECHNICAL REQUIREMENTS

The frontend MUST communicate with the backend through defined APIs.

The frontend MUST NOT:

* Calculate official risk scores.
* Run the authoritative risk algorithm.
* Store API secrets.
* Directly call private backend/provider credentials.
* Invent route data.
* Invent facility data.

---

# 8. FRONTEND MODULES

Recommended modules:

```text
frontend/
├── pages/
│   ├── Home
│   ├── RouteAnalysis
│   └── RouteDetails
│
├── components/
│   ├── SearchForm
│   ├── Map
│   ├── RouteCard
│   ├── RouteList
│   ├── HazardMarker
│   ├── FacilityMarker
│   ├── RiskSummary
│   ├── FacilitySummary
│   └── AIExplanation
│
├── services/
│   ├── routeApi
│   ├── analysisApi
│   ├── facilityApi
│   └── llmApi
│
├── state/
├── types/
├── utils/
└── assets/
```

---

# 9. SOURCE / DESTINATION INPUT

The frontend MUST provide:

```text
source
destination
```

Each selected location should resolve to:

```text
latitude
longitude
display_name
```

The frontend should not trust arbitrary user-provided coordinates without backend validation.

---

# 10. ROUTE REQUEST

Example request:

```json
{
  "source": {
    "latitude": 12.9,
    "longitude": 74.8
  },
  "destination": {
    "latitude": 12.91,
    "longitude": 74.85
  }
}
```

The exact coordinate values are examples only.

---

# 11. ROUTE RESPONSE

The backend should return a normalized internal representation.

Example:

```json
{
  "request_id": "req_123",
  "routes": [
    {
      "route_id": "route_1",
      "distance_km": 8.2,
      "duration_minutes": 19,
      "geometry": {},
      "segments": []
    }
  ]
}
```

---

# 12. ROUTE NORMALIZATION

Routing providers may return different schemas.

The system MUST normalize them into one internal representation.

Provider-specific fields should not leak throughout the entire application.

Recommended internal model:

```text
Route
├── route_id
├── request_id
├── distance_meters
├── duration_seconds
├── geometry
├── coordinates
├── segments
├── provider
├── provider_route_id
└── metadata
```

---

# 13. ROUTE SEGMENT MODEL

Each route should be divided into segments.

Recommended:

```text
Route
  |
  +-- Segment 1
  +-- Segment 2
  +-- Segment 3
  +-- ...
```

Segment:

```json
{
  "segment_id": "seg_001",
  "route_id": "route_1",
  "sequence": 1,
  "geometry": {},
  "coordinates": []
}
```

The sequence field MUST preserve route order.

---

# 14. ROUTE GEOMETRY

Route geometry should be stored in a standard internal format.

Possible representations:

* Polyline
* GeoJSON LineString
* Coordinate array

The system should use one canonical internal format.

Provider-specific geometry should be converted during normalization.

---

# 15. ROAD IMAGE PIPELINE

The image pipeline is responsible for obtaining road images associated with route segments.

Pipeline:

```text
Route
 ↓
Segment
 ↓
Image Search / Collection
 ↓
Image Validation
 ↓
Image Metadata
 ↓
OpenCV
 ↓
YOLO11
```

---

# 16. IMAGE METADATA

Every usable image should have:

```text
image_id
route_id
segment_id
source
latitude
longitude
timestamp
file_reference
width
height
format
processing_status
```

Where a field is unavailable, the system MUST use an explicit null/unavailable state rather than fabricated information.

---

# 17. IMAGE VALIDATION

The system MUST validate:

* File existence
* MIME type
* Extension
* File size
* Image readability
* Image dimensions
* Corruption

Unsupported images should be marked:

```text
invalid
```

rather than passed to the ML pipeline.

---

# 18. IMAGE QUALITY

The pipeline should optionally assess:

* Resolution
* Blur
* Exposure
* Corruption
* Excessive occlusion

Low-quality images may be excluded from inference.

The reason should be recorded where practical.

---

# 19. OPENCV PIPELINE

OpenCV is responsible for preprocessing.

Recommended pipeline:

```text
Input Image
    ↓
Read
    ↓
Validate
    ↓
Resize
    ↓
Color Conversion
    ↓
Optional Noise Reduction
    ↓
Optional Contrast Enhancement
    ↓
Normalization
    ↓
YOLO11 Input
```

Preprocessing MUST be compatible with the trained model.

Do not add transformations that significantly alter model assumptions without validation.

---

# 20. OPENCV RESPONSIBILITY BOUNDARY

OpenCV MUST NOT be described as:

```text
"the AI model that detects potholes"
```

unless an actual OpenCV-based detection algorithm is implemented.

OpenCV:

```text
preprocesses images
```

YOLO11:

```text
detects trained object classes
```

---

# 21. YOLO11 MODEL REQUIREMENTS

The production application MUST load a trained YOLO11 model.

Recommended configuration:

```text
YOLO_MODEL_PATH
YOLO_MODEL_VERSION
YOLO_CONFIDENCE_THRESHOLD
YOLO_IOU_THRESHOLD
```

Exact configuration names may differ.

---

# 22. YOLO INFERENCE

Input:

```text
Preprocessed Image
```

Output:

```text
Detection[]
```

Each detection:

```json
{
  "class_id": 0,
  "class_name": "pothole",
  "confidence": 0.87,
  "bounding_box": {
    "x1": 100,
    "y1": 120,
    "x2": 300,
    "y2": 280
  }
}
```

The example values are illustrative.

---

# 23. MODEL CLASS REQUIREMENT

The application MUST obtain the actual class list from the trained model/dataset configuration.

Do not hard-code unsupported classes.

Example:

```text
dataset classes
        ↓
model classes
        ↓
application classes
```

These three representations MUST remain consistent.

---

# 24. YOLO CONFIDENCE

Detections below the configured confidence threshold may be rejected.

Example:

```text
confidence >= configured_threshold
```

The threshold MUST be configurable.

It MUST NOT be randomly changed by the AI agent.

---

# 25. YOLO MODEL VERSIONING

Each inference result should identify:

```text
model_name
model_version
dataset_version
confidence_threshold
```

Example:

```json
{
  "model_name": "SafeRoute-YOLO11",
  "model_version": "v1.0",
  "dataset_version": "road-hazards-v1"
}
```

---

# 26. HAZARD DETECTION DATA MODEL

Recommended:

```text
HazardDetection
├── hazard_id
├── image_id
├── route_id
├── segment_id
├── hazard_type
├── confidence
├── bounding_box
├── latitude
├── longitude
├── model_version
└── created_at
```

---

# 27. HAZARD DUPLICATION

The same physical hazard can appear in multiple images.

Therefore:

```text
Image Detection
≠
Unique Physical Hazard
```

The aggregation system should use:

* Geographic proximity
* Segment association
* Image overlap
* Detection type
* Bounding-box information where useful

to reduce duplicate counting.

---

# 28. HAZARD AGGREGATION PIPELINE

```text
YOLO Detection
      ↓
Normalize
      ↓
Associate Route
      ↓
Associate Segment
      ↓
Associate Coordinates
      ↓
Duplicate Analysis
      ↓
Cluster
      ↓
Unique Hazard
      ↓
Route Summary
```

---

# 29. HAZARD SUMMARY

Example:

```json
{
  "potholes": 3,
  "road_cracks": 2,
  "damaged_roads": 1,
  "obstacles": 1,
  "debris": 0
}
```

Only actual detected/aggregated hazards should appear.

---

# 30. RISK ENGINE

The Risk Engine MUST be independent of the LLM.

Input:

```text
Aggregated Hazards
+
Hazard Metadata
+
Confidence
+
Severity
+
Exposure
+
Route Metrics
```

Output:

```text
risk_score
risk_components
```

---

# 31. RISK ENGINE INTERFACE

Conceptual interface:

```python
calculate_route_risk(
    hazards,
    route_length,
    exposure,
    configuration
)
```

The exact implementation depends on the backend language.

---

# 32. RISK CALCULATION

Conceptual formula:

```text
Risk =
Σ(
    Hazard Weight
    × Severity
    × Confidence
    × Exposure
)
```

The exact mathematical implementation MUST be documented in:

```text
docs/RISK_ENGINE.md
```

---

# 33. RISK DETERMINISM

Given:

```text
same input
+
same configuration
+
same model output
```

the Risk Engine MUST produce:

```text
same result
```

unless a documented stochastic component is deliberately introduced.

---

# 34. RISK SCORE NORMALIZATION

The system may normalize risk to:

```text
0–100
```

The normalization function MUST be consistent.

The system MUST handle:

```text
minimum
maximum
empty hazard set
missing data
extreme values
```

---

# 35. RISK DATA RESPONSE

Example:

```json
{
  "risk_score": 28,
  "risk_status": "calculated",
  "hazard_count": 7,
  "risk_components": {
    "potholes": 12,
    "road_cracks": 6,
    "obstacles": 5,
    "other": 5
  }
}
```

The exact component representation may differ.

---

# 36. FACILITY ENGINE

The Facility Engine is independent of the Hazard/Risk Engine.

It is responsible for finding facilities near route geometry.

Required categories:

```text
hospital
medical_store
restaurant
hotel
petrol_pump
police_station
```

---

# 37. FACILITY SEARCH ALGORITHM

Recommended process:

```text
Route Geometry
      ↓
Generate Search Corridor
      ↓
Query Facility Provider
      ↓
Normalize Results
      ↓
Remove Duplicates
      ↓
Calculate Distance
      ↓
Categorize
      ↓
Aggregate
```

---

# 38. FACILITY CORRIDOR

The search should use a configurable distance from the route.

Example:

```text
route
 |<---- radius ---->|
```

Configuration:

```text
FACILITY_SEARCH_RADIUS_KM
```

The exact production value should be configurable and empirically evaluated.

---

# 39. FACILITY DEDUPLICATION

Providers may return the same facility multiple times.

Deduplication may use:

* Provider ID
* Coordinates
* Name similarity
* Address

Provider IDs should be preferred where available.

---

# 40. FACILITY DISTANCE

For each facility:

```text
facility
    ↓
nearest route point
    ↓
distance from route
```

The system should calculate route-relative distance using appropriate geographic distance calculations.

Straight-line distance should not be incorrectly described as driving distance.

---

# 41. FACILITY RESPONSE

Example:

```json
{
  "hospitals": {
    "count": 3,
    "nearest_distance_km": 0.8
  },
  "medical_stores": {
    "count": 7,
    "nearest_distance_km": 0.2
  },
  "restaurants": {
    "count": 15,
    "nearest_distance_km": 0.1
  },
  "hotels": {
    "count": 5,
    "nearest_distance_km": 0.6
  },
  "petrol_pumps": {
    "count": 2,
    "nearest_distance_km": 0.9
  },
  "police_stations": {
    "count": 1,
    "nearest_distance_km": 1.2
  }
}
```

These values are examples only.

---

# 42. FACILITY FAILURE

If the facility provider fails:

```json
{
  "status": "unavailable",
  "reason": "provider_error"
}
```

The system MUST NOT return fabricated facility values.

---

# 43. ROUTE PROFILE ENGINE

The Route Profile Engine combines:

```text
Route Metadata
+
Hazard Analysis
+
Risk Analysis
+
Facility Analysis
+
Processing Status
```

It does not independently calculate risk.

---

# 44. ROUTE PROFILE STRUCTURE

Recommended:

```json
{
  "route_id": "route_1",

  "route": {
    "distance_km": 8.2,
    "duration_minutes": 19
  },

  "safety": {
    "risk_score": 28,
    "hazards": {}
  },

  "facilities": {},

  "analysis": {
    "images_analyzed": 15,
    "segments_analyzed": 24,
    "status": "completed"
  }
}
```

---

# 45. LLM SERVICE

The LLM service receives structured data from the Route Profile Engine.

The frontend MUST NOT directly construct the authoritative LLM data payload.

Recommended flow:

```text
Database / Analysis
       ↓
Route Profile
       ↓
LLM Service
       ↓
Structured Prompt
       ↓
LLM Provider
       ↓
Validated Explanation
       ↓
Frontend
```

---

# 46. LLM INPUT

The LLM input should contain only verified information.

Example:

```json
{
  "route_id": "route_1",
  "distance_km": 8.2,
  "duration_minutes": 19,
  "risk_score": 28,
  "hazards": {
    "potholes": 3,
    "road_cracks": 2
  },
  "facilities": {
    "hospitals": 3,
    "medical_stores": 7
  }
}
```

---

# 47. LLM SYSTEM INSTRUCTION

The LLM should receive instructions equivalent to:

```text
You are the explanation layer of SafeRoute AI.

Use only the structured data supplied by the backend.

Do not invent information.

Do not modify numerical values.

Do not calculate a new risk score.

Do not invent missing facilities.

Do not claim that a route is completely safe.

If information is unavailable, clearly state that it is unavailable.

Explain the provided route information in clear language.
```

---

# 48. LLM OUTPUT VALIDATION

LLM output should be validated before returning to the frontend where practical.

The system should detect obvious unsupported numerical claims.

The LLM MUST NOT be treated as an authoritative data source.

---

# 49. API ARCHITECTURE

Recommended API layers:

```text
HTTP Layer
    ↓
Validation
    ↓
Controller
    ↓
Service
    ↓
Repository / Provider
```

Controllers should remain thin.

Business logic should live in services.

Database operations should be isolated in repositories/data-access modules where appropriate.

---

# 50. API ENDPOINTS

## Create Routes

```http
POST /api/routes
```

Request:

```json
{
  "source": {
    "latitude": 12.9,
    "longitude": 74.8
  },
  "destination": {
    "latitude": 12.91,
    "longitude": 74.85
  }
}
```

Response:

```json
{
  "request_id": "req_123",
  "routes": []
}
```

---

# 51. GET ROUTE

```http
GET /api/routes/{route_id}
```

Returns normalized route data.

---

# 52. START ANALYSIS

```http
POST /api/routes/{route_id}/analyze
```

Starts or requests route analysis.

Possible response:

```json
{
  "route_id": "route_1",
  "status": "processing"
}
```

---

# 53. GET HAZARDS

```http
GET /api/routes/{route_id}/hazards
```

Returns hazard information.

---

# 54. GET FACILITIES

```http
GET /api/routes/{route_id}/facilities
```

Returns nearby facilities.

---

# 55. GET ANALYSIS

```http
GET /api/routes/{route_id}/analysis
```

Returns route analysis.

---

# 56. LLM EXPLANATION

```http
POST /api/llm/explanation
```

The endpoint should preferably accept a route-analysis identifier rather than arbitrary client-generated numerical values.

This reduces the possibility of users manipulating the authoritative analysis input.

---

# 57. API VALIDATION

Backend MUST validate:

* Latitude
* Longitude
* Required fields
* Data types
* Coordinate ranges
* Route IDs
* Request sizes

Latitude:

```text
-90 <= latitude <= 90
```

Longitude:

```text
-180 <= longitude <= 180
```

---

# 58. API ERROR FORMAT

Use a consistent error structure.

Example:

```json
{
  "error": {
    "code": "ROUTE_NOT_FOUND",
    "message": "No route was found for the requested locations.",
    "request_id": "req_123"
  }
}
```

Do not expose stack traces to end users.

---

# 59. DATABASE ARCHITECTURE

Recommended logical model:

```text
users
  |
  v
route_requests
  |
  v
routes
  |
  v
route_segments
  |
  v
road_images
  |
  v
hazards

routes
  |
  +------ facilities
  |
  +------ route_facilities
  |
  +------ route_analysis

model_versions
```

---

# 60. DATABASE TABLE: USERS

Potential fields:

```text
id
email
password_hash
created_at
updated_at
```

Only implement authentication fields if authentication is part of the actual product scope.

---

# 61. DATABASE TABLE: ROUTE_REQUESTS

```text
id
source_latitude
source_longitude
destination_latitude
destination_longitude
status
created_at
updated_at
```

---

# 62. DATABASE TABLE: ROUTES

```text
id
request_id
provider
provider_route_id
distance_meters
duration_seconds
geometry
status
created_at
updated_at
```

---

# 63. DATABASE TABLE: ROUTE_SEGMENTS

```text
id
route_id
sequence
geometry
start_latitude
start_longitude
end_latitude
end_longitude
status
```

---

# 64. DATABASE TABLE: ROAD_IMAGES

```text
id
route_id
segment_id
source
latitude
longitude
timestamp
file_reference
width
height
format
processing_status
created_at
```

---

# 65. DATABASE TABLE: HAZARDS

```text
id
route_id
segment_id
image_id
hazard_type
confidence
bounding_box
latitude
longitude
model_version
created_at
```

---

# 66. DATABASE TABLE: FACILITIES

```text
id
provider
provider_id
name
category
latitude
longitude
address
phone
metadata
created_at
updated_at
```

---

# 67. DATABASE TABLE: ROUTE FACILITIES

This table represents route-to-facility association.

```text
id
route_id
facility_id
distance_from_route
nearest_segment_id
created_at
```

---

# 68. DATABASE TABLE: ROUTE ANALYSIS

```text
id
route_id
risk_score
hazard_count
images_analyzed
segments_analyzed
analysis_status
model_version
created_at
updated_at
```

---

# 69. MODEL VERSIONS TABLE

```text
id
model_name
model_version
dataset_version
configuration
created_at
```

---

# 70. DATABASE INDEXING

Potential indexes:

```text
routes.request_id

route_segments.route_id

road_images.route_id

road_images.segment_id

hazards.route_id

hazards.segment_id

hazards.hazard_type

facilities.category

facilities.latitude
facilities.longitude

route_facilities.route_id
```

Geospatial indexing should be considered if supported by the chosen database.

---

# 71. TRANSACTION REQUIREMENTS

Database transactions should be used when multiple related records must remain consistent.

Example:

```text
Create Route
      ↓
Create Segments
      ↓
Commit
```

If a critical operation fails, the system should avoid leaving inconsistent partial data.

---

# 72. CONFIGURATION MANAGEMENT

Configuration MUST be externalized.

Potential variables:

```text
APP_ENV

DATABASE_URL

ROUTING_PROVIDER_URL

ROUTING_PROVIDER_KEY

FACILITY_PROVIDER_URL

FACILITY_PROVIDER_KEY

YOLO_MODEL_PATH

YOLO_MODEL_VERSION

YOLO_CONFIDENCE_THRESHOLD

YOLO_IOU_THRESHOLD

FACILITY_SEARCH_RADIUS_KM

MAX_CANDIDATE_ROUTES

LLM_PROVIDER

LLM_MODEL

LLM_API_KEY

REQUEST_TIMEOUT

IMAGE_MAX_SIZE
```

Never commit secrets.

---

# 73. ENVIRONMENT SEPARATION

The project should support:

```text
development
testing
production
```

Configuration should be environment-specific.

---

# 74. SECRETS

Secrets MUST NOT appear in:

* Source code
* Frontend JavaScript
* Git repository
* Logs
* Error responses
* Screenshots
* Documentation

Use:

```text
.env
```

or an appropriate secrets-management system.

---

# 75. SECURITY REQUIREMENTS

The backend MUST implement appropriate:

* Authentication where required
* Authorization
* Input validation
* Rate limiting
* Request size limits
* File validation
* API key protection
* Error sanitization

---

# 76. FILE UPLOAD SECURITY

If users can upload images:

Validate:

```text
MIME type
extension
file size
dimensions
content
```

Do not trust filename extensions alone.

---

# 77. IMAGE STORAGE

The application should not unnecessarily store every temporary image permanently.

Define lifecycle:

```text
Collected
 ↓
Validated
 ↓
Processed
 ↓
Analyzed
 ↓
Stored / Deleted according to policy
```

Storage policy should be configurable.

---

# 78. LOGGING

Every major request should have a request ID.

Example:

```text
request_id=req_123
route_id=route_1
stage=YOLO_INFERENCE
duration=1.82s
status=success
```

---

# 79. LOG LEVELS

Recommended:

```text
DEBUG
INFO
WARNING
ERROR
```

Production logs should not expose sensitive data.

---

# 80. ERROR CLASSIFICATION

Recommended categories:

```text
VALIDATION_ERROR
ROUTING_ERROR
IMAGE_ERROR
OPENCV_ERROR
YOLO_ERROR
HAZARD_ERROR
RISK_ERROR
FACILITY_ERROR
DATABASE_ERROR
LLM_ERROR
TIMEOUT_ERROR
RATE_LIMIT_ERROR
INTERNAL_ERROR
```

---

# 81. OBSERVABILITY

Track:

```text
route generation latency
image processing latency
YOLO inference latency
facility query latency
risk calculation latency
LLM latency
total request latency
error rate
```

---

# 82. ASYNCHRONOUS PROCESSING

Road-image analysis may be computationally expensive.

If analysis cannot reasonably complete during a synchronous request, use:

```text
POST /analyze
      ↓
Job Created
      ↓
Background Processing
      ↓
Status Updates
      ↓
Completed Result
```

Do not introduce a message queue unless the project's actual workload requires it.

---

# 83. ANALYSIS JOB MODEL

Possible:

```text
analysis_job_id
route_id
status
stage
progress
started_at
completed_at
error
```

Status:

```text
queued
processing
completed
partial
failed
```

---

# 84. ANALYSIS PIPELINE STATE MACHINE

```text
PENDING
   ↓
ROUTE_READY
   ↓
COLLECTING_IMAGES
   ↓
IMAGES_READY
   ↓
PREPROCESSING
   ↓
YOLO_INFERENCE
   ↓
HAZARD_AGGREGATION
   ↓
RISK_CALCULATION
   ↓
FACILITY_ANALYSIS
   ↓
ROUTE_PROFILE_READY
   ↓
LLM_EXPLANATION
   ↓
COMPLETED
```

Failure at an optional stage may produce:

```text
PARTIAL
```

rather than total failure.

---

# 85. CACHING REQUIREMENTS

Potential cache keys:

```text
route geometry hash
+
provider
+
model version
+
configuration
```

For YOLO:

```text
image hash
+
model version
+
inference configuration
```

For facilities:

```text
route geometry hash
+
facility category
+
search radius
+
provider
```

---

# 86. CACHE INVALIDATION

Invalidate or bypass cache when:

* Model changes
* Risk configuration changes
* Route changes
* Facility radius changes
* Provider changes
* Data freshness requirements expire

---

# 87. PERFORMANCE OPTIMIZATION

Optimization priorities:

```text
1. Avoid unnecessary API calls
2. Avoid duplicate image processing
3. Batch YOLO inference
4. Cache expensive results
5. Reduce image size appropriately
6. Optimize database queries
7. Avoid unnecessary LLM calls
```

Do not optimize prematurely.

---

# 88. CONCURRENCY

Independent route analyses may be processed concurrently.

Example:

```text
Route 1 ──┐
Route 2 ──┤
Route 3 ──┼── Parallel analysis
Route 4 ──┘
```

The system MUST respect:

* API rate limits
* CPU/GPU capacity
* memory limits
* provider limits

---

# 89. RESOURCE LIMITS

Configuration should define:

```text
MAX_ROUTES
MAX_IMAGES_PER_ROUTE
MAX_IMAGE_SIZE
MAX_CONCURRENT_INFERENCE
MAX_FACILITY_RESULTS
REQUEST_TIMEOUT
```

Exact values should be determined through testing.

---

# 90. YOLO GPU/CPU SUPPORT

The inference service should support:

```text
CPU
```

and optionally:

```text
GPU
```

The system should automatically or configurably select the execution device.

Do not assume a GPU is always available.

---

# 91. MODEL LOADING

The YOLO model should preferably be loaded once per inference process rather than reloaded for every image.

Bad:

```text
Request
 ↓
Load Model
 ↓
Analyze Image
 ↓
Unload Model
```

Preferred:

```text
Application Start
 ↓
Load Model
 ↓
Multiple Inferences
```

---

# 92. MODEL FAILURE

If model loading fails:

```text
YOLO status = unavailable
```

The system MUST:

* Log the error
* Mark analysis appropriately
* Avoid fabricated detections
* Return a meaningful error/partial state

---

# 93. FACILITY PROVIDER ABSTRACTION

The application should isolate external facility providers behind an internal interface.

Conceptual:

```python
FacilityProvider
    ├── search()
    ├── normalize()
    └── health_check()
```

This makes future provider replacement easier.

---

# 94. ROUTING PROVIDER ABSTRACTION

Similarly:

```python
RoutingProvider
    ├── geocode()
    ├── route()
    └── normalize()
```

Provider-specific implementation should remain isolated.

---

# 95. LLM PROVIDER ABSTRACTION

The LLM integration should ideally be behind a service layer.

Conceptual:

```python
LLMService
    ├── generate_explanation()
    ├── validate_output()
    └── handle_error()
```

The rest of the application should not depend directly on provider-specific SDK calls.

---

# 96. API RATE LIMITS

External providers may enforce rate limits.

The system should:

* Respect provider limits
* Handle HTTP 429
* Retry only when appropriate
* Use exponential backoff where appropriate
* Avoid infinite retries
* Cache results

---

# 97. RETRY POLICY

Retries should be used only for transient failures.

Possible retry cases:

```text
temporary network error
timeout
provider 5xx
```

Avoid retrying:

```text
invalid API key
invalid request
invalid coordinates
unsupported request
```

---

# 98. TIMEOUT POLICY

Every external request should have a timeout.

No external API call should be allowed to hang indefinitely.

---

# 99. FRONTEND STATE MODEL

Recommended route-analysis states:

```text
idle
searching
routes_loaded
analysis_pending
analyzing
completed
partial
failed
```

---

# 100. FRONTEND DATA MODEL

Example:

```typescript
type Route = {
  routeId: string;
  distanceKm: number;
  durationMinutes: number;
  geometry: unknown;
  safety?: SafetyAnalysis;
  facilities?: FacilityAnalysis;
  analysisStatus: AnalysisStatus;
};
```

The actual implementation language may differ.

---

# 101. HAZARD UI

Hazard markers should contain:

```text
hazard type
confidence if appropriate
location
route
```

Example:

```text
Pothole
Confidence: 87%
```

Confidence should be presented carefully and not misrepresented as probability of a real-world hazard.

---

# 102. FACILITY UI

Facility markers should show:

```text
Name
Category
Distance from route
Address where available
```

The UI must distinguish:

```text
provider data
```

from:

```text
AI-generated explanation
```

---

# 103. ROUTE ANALYSIS UI

Recommended layout:

```text
┌──────────────────────────────────┐
│ Route 1                          │
│ 8.2 km | 19 min                  │
├──────────────────────────────────┤
│ Safety Analysis                  │
│ Risk Score: 28                   │
│                                  │
│ Potholes: 3                      │
│ Cracks: 2                        │
├──────────────────────────────────┤
│ Nearby Facilities                │
│ Hospitals: 3                     │
│ Medical Stores: 7                │
│ Petrol Pumps: 2                  │
├──────────────────────────────────┤
│ AI Explanation                   │
└──────────────────────────────────┘
```

---

# 104. ACCESSIBILITY

Frontend should support:

* Keyboard navigation
* Readable contrast
* Labels for controls
* Accessible map controls where possible
* Screen-reader-friendly route information
* Clear error messages

---

# 105. RESPONSIVE DESIGN

The frontend should work on:

```text
Desktop
Tablet
Mobile
```

The map and route cards must remain usable on smaller screens.

---

# 106. API VERSIONING

If public API compatibility becomes important, use versioning:

```text
/api/v1/routes
```

Do not introduce API versioning complexity unless needed by the current architecture.

---

# 107. TESTING ARCHITECTURE

Testing layers:

```text
Unit Tests
    ↓
Integration Tests
    ↓
API Tests
    ↓
ML Pipeline Tests
    ↓
End-to-End Tests
```

---

# 108. UNIT TEST REQUIREMENTS

Unit tests MUST cover:

* Route normalization
* Coordinate validation
* Hazard aggregation
* Risk calculation
* Facility aggregation
* LLM input preparation
* Error mapping

---

# 109. ML TEST REQUIREMENTS

Test:

* Model loading
* Input preprocessing
* Detection parsing
* Class mapping
* Confidence filtering
* Empty detection results
* Invalid images
* Model failure

---

# 110. RISK ENGINE TESTS

Test:

```text
No hazards
One hazard
Multiple hazards
Low confidence
High confidence
Different hazard types
Maximum values
Missing optional values
```

---

# 111. FACILITY TESTS

Test:

```text
No facilities
One facility
Multiple facilities
Duplicate facilities
Different categories
Provider failure
Missing coordinates
```

---

# 112. API TESTS

Test:

```text
Valid request
Invalid request
Missing fields
Invalid coordinates
No route
Provider failure
Timeout
Rate limit
```

---

# 113. END-TO-END TEST

Minimum complete flow:

```text
Enter Source
       ↓
Enter Destination
       ↓
Generate Routes
       ↓
Select Route
       ↓
Run Analysis
       ↓
Process Images
       ↓
YOLO Detection
       ↓
Hazard Aggregation
       ↓
Risk Calculation
       ↓
Facility Search
       ↓
Route Profile
       ↓
LLM Explanation
       ↓
Display Result
```

---

# 114. TEST DATA

The project should maintain test fixtures for:

* Routes
* Images
* YOLO outputs
* Hazards
* Facilities
* Risk calculations
* LLM structured input

Do not depend exclusively on live external APIs for automated tests.

---

# 115. EXTERNAL API MOCKING

Automated tests should mock external:

* Routing APIs
* Facility APIs
* LLM APIs

where appropriate.

This improves:

* Speed
* Reliability
* Reproducibility
* Cost control

---

# 116. DATA VALIDATION

Every external provider response should be validated before entering the internal system.

Flow:

```text
External API
     ↓
Schema Validation
     ↓
Normalization
     ↓
Internal Model
```

Never assume external responses are always valid.

---

# 117. SCHEMA VALIDATION

Use typed models/schema validation where supported.

Validate:

* Required fields
* Types
* Coordinate ranges
* Enum values
* Numeric ranges

---

# 118. TYPE SAFETY

Where supported by the chosen language/framework:

* Use explicit types.
* Avoid unnecessary `any`.
* Define API request/response types.
* Define domain models.
* Define ML output models.

---

# 119. CODE QUALITY

Code should:

* Have clear naming.
* Use small functions.
* Avoid duplicated business logic.
* Separate concerns.
* Avoid unnecessary abstraction.
* Include comments only where they add value.

---

# 120. COMMENTING RULE

Comments should explain:

```text
why
```

rather than merely:

```text
what
```

Bad:

```python
# Add 1 to count
count += 1
```

Better:

```python
# Ignore duplicate detections from overlapping images.
```

---

# 121. ERROR HANDLING CODE

Do not silently swallow exceptions.

Bad:

```python
try:
    process()
except:
    pass
```

Preferred:

```text
Catch
 ↓
Log
 ↓
Classify
 ↓
Recover or fail explicitly
```

---

# 122. EXTERNAL SERVICE HEALTH

Where appropriate, expose internal health checks:

```text
/api/health
```

Possible components:

```text
database
routing provider
facility provider
YOLO model
LLM provider
```

Do not expose sensitive provider credentials.

---

# 123. DEPLOYMENT ARCHITECTURE

Initial deployment may use:

```text
Frontend
   ↓
Backend
   ↓
Database
   ↓
ML inference
```

External services:

```text
Routing Provider
Facility Provider
LLM Provider
```

Avoid unnecessary Kubernetes/microservices for the initial version.

---

# 124. CONTAINERIZATION

Docker may be used for reproducible environments.

Potential services:

```text
frontend
backend
database
```

ML inference can remain within backend initially if resource requirements permit.

Separate inference service may be introduced later if justified.

---

# 125. ENVIRONMENT

Development environment should provide:

```text
local frontend
local backend
local database
local model
mock/external providers
```

---

# 126. CI/CD

If CI/CD is implemented, pipeline should include:

```text
Install dependencies
      ↓
Lint
      ↓
Unit tests
      ↓
Integration tests
      ↓
Build
      ↓
Security checks
      ↓
Deploy
```

---

# 127. GIT REQUIREMENTS

Use meaningful commits.

Example:

```text
feat: add route normalization
feat: integrate YOLO11 inference
feat: add facility analysis
fix: handle missing route geometry
test: add risk engine tests
docs: update architecture
```

Avoid commits such as:

```text
update
final
new
changes
test123
```

---

# 128. BRANCHING

Recommended:

```text
main
develop
feature/*
fix/*
```

The exact branching model may be simplified for a college project.

---

# 129. MIGRATION RULE

Database schema changes MUST be versioned through migrations.

Do not manually modify production databases without migration tracking.

---

# 130. BACKWARD COMPATIBILITY

Existing APIs should not be broken unnecessarily.

If an API contract changes:

1. Identify consumers.
2. Update backend.
3. Update frontend.
4. Update tests.
5. Update documentation.

---

# 131. DATA CONSISTENCY

The following IDs must remain consistent throughout the pipeline:

```text
request_id
route_id
segment_id
image_id
hazard_id
facility_id
analysis_id
model_version
```

Example:

```text
route_1
  ↓
segment_03
  ↓
image_17
  ↓
hazard_91
```

---

# 132. TRACEABILITY

A hazard shown to the user should ideally be traceable to:

```text
Hazard
 ↓
Image
 ↓
Segment
 ↓
Route
 ↓
Route Request
```

A risk score should be traceable to:

```text
Risk Score
 ↓
Risk Calculation
 ↓
Aggregated Hazards
 ↓
Model Version
```

---

# 133. FACILITY TRACEABILITY

Facility information should be traceable to:

```text
Facility
 ↓
Provider
 ↓
Provider ID
 ↓
Route
 ↓
Search Configuration
```

---

# 134. LLM TRACEABILITY

An explanation should be traceable to:

```text
LLM Explanation
 ↓
Route Profile
 ↓
Analysis ID
 ↓
Underlying Data
```

This is important for debugging hallucinations or incorrect output.

---

# 135. DATA FRESHNESS

Data should have timestamps where relevant.

Examples:

```text
road image timestamp
facility data timestamp
route request timestamp
analysis timestamp
model version
```

The system should avoid implying that old imagery represents current road conditions.

---

# 136. ROAD IMAGE LIMITATION

If the system does not have sufficiently recent imagery, the UI should communicate the limitation where relevant.

Example:

```text
Road-condition analysis is based on available imagery and may not reflect
current conditions.
```

---

# 137. FACILITY DATA LIMITATION

Facility results depend on external provider coverage.

The system should not claim:

```text
"There are no hospitals nearby"
```

when the provider simply returned no data due to an error.

Distinguish:

```text
zero results
```

from:

```text
provider unavailable
```

---

# 138. RISK DATA LIMITATION

A route with a low project risk score MUST NOT automatically be described as:

```text
completely safe
```

The score represents the implemented analytical model and available data.

---

# 139. LLM SAFETY

The LLM must not produce:

* Safety guarantees
* Unsupported emergency instructions
* Fabricated statistics
* Fabricated road conditions
* Fabricated facility availability

The LLM should explain rather than invent.

---

# 140. FAILURE ISOLATION

Subsystem failures should be isolated.

Example:

```text
Routing success
      ↓
YOLO failure
      ↓
Facility success
```

The system may return:

```text
Route information: available
Hazard analysis: unavailable
Facilities: available
```

rather than failing the entire request.

---

# 141. PARTIAL ANALYSIS RESPONSE

Example:

```json
{
  "status": "partial",

  "route": {
    "distance_km": 8.2,
    "duration_minutes": 19
  },

  "safety": {
    "status": "unavailable"
  },

  "facilities": {
    "status": "completed"
  }
}
```

---

# 142. AI AGENT IMPLEMENTATION RULES

Any AI coding agent working on this repository MUST:

1. Read `MASTER_RULES.md`.
2. Read relevant PRD sections.
3. Read relevant TRD sections.
4. Inspect existing implementation.
5. Identify affected components.
6. Make the smallest correct change.
7. Run relevant tests.
8. Verify API/data compatibility.
9. Report changes.

---

# 143. AI AGENT MUST NOT

The AI agent MUST NOT:

* Invent requirements.
* Replace the architecture.
* Introduce unrelated technology.
* Replace YOLO11 with another model without approval.
* Replace the routing engine without approval.
* Convert the LLM into the risk engine.
* Combine facilities into the safety score without approval.
* Fabricate missing data.
* Rewrite the whole project unnecessarily.
* Delete working modules.
* Change database technology without approval.

---

# 144. ARCHITECTURAL CHANGE CONTROL

The following require explicit project-owner approval:

```text
Change programming language
Change frontend framework
Change backend framework
Change database
Replace YOLO11
Replace routing architecture
Change risk algorithm
Change facility architecture
Introduce microservices
Introduce message queue
Introduce Kubernetes
Change public API contracts
Change core database schema
```

---

# 145. FEATURE DEVELOPMENT WORKFLOW

Every feature should follow:

```text
Requirement
    ↓
PRD Check
    ↓
TRD Check
    ↓
Existing Code Inspection
    ↓
Architecture Impact
    ↓
Implementation Plan
    ↓
Code
    ↓
Tests
    ↓
Verification
    ↓
Documentation
```

---

# 146. NEW FEATURE GATE

Before adding a feature, answer:

```text
1. Why does SafeRoute AI need this?
2. Which PRD requirement does it satisfy?
3. Which TRD component owns it?
4. Does an existing component already solve it?
5. Does it change the database?
6. Does it change an API?
7. Does it introduce a dependency?
8. Does it affect security?
9. Does it affect performance?
10. Does it require architecture approval?
```

---

# 147. CODE CHANGE SCOPE

A feature should modify only the files required to implement it.

Do not perform unrelated:

* Formatting
* Refactoring
* Renaming
* Dependency upgrades
* Architecture changes

in the same change unless required.

---

# 148. TECHNICAL DEBT

Technical debt should be documented rather than silently ignored.

Example:

```text
TODO:
Replace temporary in-memory cache with Redis if deployment scale requires it.
```

Do not prematurely implement infrastructure that is not currently needed.

---

# 149. TEMPORARY IMPLEMENTATIONS

Temporary implementations MUST be clearly marked.

Example:

```text
DEMO IMPLEMENTATION
NOT FOR PRODUCTION
```

A temporary/mock provider MUST NOT be mistaken for a real provider.

---

# 150. MOCK DATA

Mock data may be used during development.

However:

* It must be clearly labeled.
* It must not be presented as real analysis.
* Production code should use real provider/model data.
* Mock values should not silently enter production.

---

# 151. SAMPLE DATA

Example/sample route results in documentation are illustrative only.

They MUST NOT be interpreted as real system output.

---

# 152. API DOCUMENTATION

API documentation should contain:

```text
Endpoint
Method
Authentication
Request schema
Response schema
Errors
Example
```

The source of truth should be updated whenever API contracts change.

---

# 153. DATABASE DOCUMENTATION

Database documentation should contain:

* Tables
* Fields
* Types
* Relationships
* Indexes
* Constraints
* Migrations

---

# 154. ML DOCUMENTATION

ML documentation should contain:

* Dataset source
* Classes
* Annotation format
* Training configuration
* Validation metrics
* Model version
* Inference configuration
* Known limitations

Never fabricate ML metrics.

---

# 155. RISK ENGINE DOCUMENTATION

Must document:

* Formula
* Hazard weights
* Severity
* Confidence
* Exposure
* Normalization
* Missing-data handling
* Examples
* Test cases
* Limitations

---

# 156. FACILITY ENGINE DOCUMENTATION

Must document:

* Provider
* Search radius
* Categories
* Deduplication
* Distance calculation
* Result limits
* Caching
* Failure behavior

---

# 157. DEPLOYMENT DOCUMENTATION

Must document:

```text
Requirements
Environment variables
Database setup
Model setup
Frontend setup
Backend setup
Build
Run
Testing
Deployment
```

---

# 158. SYSTEM HEALTH

The application should expose a health mechanism capable of determining whether critical components are functioning.

Example:

```json
{
  "status": "healthy",
  "database": "healthy",
  "model": "loaded"
}
```

External provider checks may be separated from basic health checks to avoid unnecessary provider calls.

---

# 159. MONITORING METRICS

Recommended metrics:

```text
route_requests_total
route_generation_failures
analysis_requests_total
analysis_failures
yolo_inference_count
yolo_inference_duration
facility_requests_total
facility_failures
llm_requests_total
llm_failures
average_analysis_duration
```

---

# 160. SECURITY MONITORING

Monitor:

* Repeated failed authentication
* Excessive requests
* Invalid uploads
* Provider errors
* Unexpected payload sizes

Never log secrets.

---

# 161. BACKUP

Important persistent data should have a backup strategy appropriate to the deployment environment.

At minimum:

```text
Database backup
Model backup/versioning
Configuration backup without secrets
```

---

# 162. MODEL BACKUP

The exact model artifact used in production should be reproducible.

Track:

```text
model version
dataset version
training configuration
model file hash where appropriate
```

---

# 163. REPRODUCIBILITY

A production analysis should ideally be reproducible using:

```text
Route data
+
Image IDs
+
Model version
+
Risk configuration
+
Facility configuration
```

---

# 164. VERSION COMPATIBILITY

Track compatibility between:

```text
Frontend version
Backend version
Database schema version
Model version
Risk configuration version
```

---

# 165. SYSTEM DATA FLOW

Complete data flow:

```text
SOURCE
   |
DESTINATION
   |
   v
GEOCODING
   |
   v
ROUTING
   |
   v
ROUTE 1 ... ROUTE 4
   |
   +-----------------------------+
   |                             |
   v                             v
ROUTE GEOMETRY              ROUTE SEGMENTS
                                  |
                                  v
                           ROAD IMAGES
                                  |
                                  v
                                OPENCV
                                  |
                                  v
                               YOLO11
                                  |
                                  v
                           DETECTIONS
                                  |
                                  v
                         HAZARD AGGREGATION
                                  |
                                  v
                            RISK ENGINE
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
             FACILITY ENGINE              ROUTE METADATA
                    |                           |
                    +-------------+-------------+
                                  |
                                  v
                           ROUTE PROFILE
                                  |
                                  v
                              LLM
                                  |
                                  v
                             FRONTEND
```

---

# 166. COMPLETE ROUTE OBJECT

Recommended conceptual object:

```json
{
  "route_id": "route_1",

  "route": {
    "distance_km": 8.2,
    "duration_minutes": 19,
    "geometry": {}
  },

  "analysis": {
    "status": "completed",
    "segments_analyzed": 24,
    "images_analyzed": 15
  },

  "safety": {
    "risk_score": 28,
    "hazards": {
      "potholes": 3,
      "road_cracks": 2
    }
  },

  "facilities": {
    "hospitals": {
      "count": 3,
      "nearest_distance_km": 0.8
    }
  },

  "model": {
    "name": "SafeRoute-YOLO11",
    "version": "v1.0"
  }
}
```

---

# 167. SYSTEM INVARIANTS

The following must always remain true:

### Invariant 1

Routing generates routes.

### Invariant 2

YOLO11 generates hazard detections.

### Invariant 3

The Risk Engine calculates the authoritative project risk score.

### Invariant 4

Facilities remain separate from hazard risk.

### Invariant 5

LLM does not create authoritative numerical data.

### Invariant 6

Missing data is represented as unavailable.

### Invariant 7

No fabricated data enters production results.

### Invariant 8

Every route has a unique route ID.

### Invariant 9

Every hazard should be traceable to its source data where possible.

### Invariant 10

Model version must be traceable.

---

# 168. CRITICAL TECHNICAL RULE

The following transformation MUST NOT occur:

```text
YOLO detections
+
Hospitals
+
Restaurants
+
Hotels
+
Petrol pumps
+
Police stations
+
LLM opinion
        ↓
Random "AI Safety Score"
```

Instead:

```text
YOLO
 ↓
Hazards
 ↓
Risk Engine
 ↓
Risk Metrics


Facilities
 ↓
Accessibility / Convenience Information


LLM
 ↓
Explanation
```

---

# 169. FAILURE INTEGRITY RULE

When something fails:

```text
FAILURE
   ↓
Detect
   ↓
Classify
   ↓
Log
   ↓
Return explicit status
```

Never:

```text
FAILURE
   ↓
Invent result
```

---

# 170. TECHNICAL DEFINITION OF DONE

A technical feature is complete only when:

```text
[ ] Requirement implemented
[ ] Correct component owns implementation
[ ] Existing architecture preserved
[ ] API contract valid
[ ] Database changes migrated
[ ] Input validation implemented
[ ] Error handling implemented
[ ] Tests added/updated
[ ] Relevant tests pass
[ ] Logging implemented where required
[ ] Security reviewed
[ ] Configuration externalized
[ ] Documentation updated
[ ] No fabricated data
[ ] No unnecessary dependencies
[ ] No unrelated files modified
```

---

# 171. FINAL ARCHITECTURAL CONTRACT

SafeRoute AI MUST maintain the following technical responsibility chain:

```text
ROUTING PROVIDER
    ↓
Generates candidate routes

ROUTE NORMALIZER
    ↓
Creates internal route representation

IMAGE PIPELINE
    ↓
Obtains and validates road imagery

OPENCV
    ↓
Preprocesses images

YOLO11
    ↓
Detects trained road hazards

HAZARD ENGINE
    ↓
Aggregates detections

RISK ENGINE
    ↓
Calculates deterministic risk

FACILITY ENGINE
    ↓
Finds nearby facilities

ROUTE PROFILE ENGINE
    ↓
Combines verified route information

LLM SERVICE
    ↓
Explains verified information

FRONTEND
    ↓
Displays information to the user
```

---

# 172. FINAL AI AGENT CONTRACT

Any AI agent working inside this repository MUST treat this document as the technical implementation boundary.

Before making a significant change:

```text
READ
 ↓
UNDERSTAND
 ↓
CHECK PRD
 ↓
CHECK TRD
 ↓
CHECK MASTER RULES
 ↓
INSPECT EXISTING CODE
 ↓
PLAN
 ↓
IMPLEMENT
 ↓
TEST
 ↓
VERIFY
```

If the requested change conflicts with the architecture:

```text
STOP
 ↓
Explain conflict
 ↓
Identify affected components
 ↓
Request explicit approval
```

The AI agent MUST NOT silently redesign SafeRoute AI.

---

# END OF TECHNICAL REQUIREMENTS DOCUMENT