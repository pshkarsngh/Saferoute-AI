# SafeRoute AI

## Product Requirements Document (PRD)

**Project Name:** SafeRoute AI
**Product Type:** Intelligent Road Safety Navigation System
**Project Category:** Major College Project
**Document Version:** 1.0
**Status:** Development
**Primary Objective:** Intelligent route analysis using road-hazard detection, deterministic risk analysis, nearby facility intelligence, and grounded AI explanations.

---

# 1. DOCUMENT PURPOSE

This Product Requirements Document defines the functional, technical, and product requirements for SafeRoute AI.

This document serves as the product-level source of truth for:

* What SafeRoute AI does
* Who it is designed for
* Which features are required
* How the major components interact
* What data the system processes
* What the AI/ML components are responsible for
* What the system must and must not do
* How success is measured
* What constitutes a completed feature

All implementation decisions should remain consistent with this PRD and `MASTER_RULES.md`.

---

# 2. PRODUCT OVERVIEW

SafeRoute AI is an intelligent navigation system designed to provide users with additional road-safety information about candidate routes.

Traditional navigation systems primarily focus on:

* Distance
* Estimated travel time
* Traffic
* Basic route selection

SafeRoute AI extends route analysis by examining available road imagery using computer vision and YOLO11-based hazard detection.

The system can analyze candidate routes for road hazards such as:

* Potholes
* Road cracks
* Damaged road surfaces
* Obstacles
* Debris

The system also analyzes nearby facilities around each route, including:

* Hospitals
* Medical stores / pharmacies
* Restaurants
* Hotels
* Petrol pumps / fuel stations
* Police stations

The product does not simply produce a single opaque "AI recommendation."

Instead, SafeRoute AI presents structured evidence for each candidate route so that the user can understand:

* Route distance
* Route duration
* Detected hazards
* Risk metrics
* Number and proximity of nearby facilities
* Route-specific analysis

An LLM is used only as an explanation layer over verified backend data.

---

# 3. PRODUCT VISION

The vision of SafeRoute AI is:

> To provide navigation users with a richer understanding of road conditions and route accessibility by combining routing data, computer vision, deterministic risk analysis, nearby facility information, and grounded AI explanations.

---

# 4. PRODUCT GOALS

## 4.1 Primary Goals

The system MUST:

1. Accept source and destination.
2. Generate candidate routes.
3. Support up to four candidate routes.
4. Display candidate routes on an interactive map.
5. Collect available road imagery associated with routes.
6. Process images using OpenCV.
7. Detect road hazards using YOLO11.
8. Aggregate hazards by route and segment.
9. Calculate a deterministic road-risk score.
10. Identify nearby facilities around each route.
11. Provide route-specific safety and facility information.
12. Provide natural-language explanations using an LLM.
13. Ensure LLM responses are grounded in verified backend data.
14. Allow users to inspect route details.

---

# 5. NON-GOALS

The following are NOT primary objectives:

* Replacing Google Maps or other navigation platforms.
* Guaranteeing that a route is completely safe.
* Predicting accidents with certainty.
* Providing emergency medical services.
* Providing real-time police assistance.
* Operating petrol delivery services.
* Creating a general-purpose chatbot.
* Performing facial recognition.
* Tracking users without consent.
* Creating unrelated recommendation systems.
* Making autonomous driving decisions.

These features must not be added without explicit product approval.

---

# 6. TARGET USERS

## 6.1 General Travelers

Users who want additional information about road conditions before travelling.

## 6.2 Students

Students travelling between:

* Home
* College
* Hostel
* Internship
* Events

## 6.3 Daily Commuters

Users who frequently travel through the same routes.

## 6.4 Long-Distance Travelers

Users who want to inspect road conditions and nearby services before selecting a route.

## 6.5 Emergency-Aware Travelers

Users who may value information about nearby:

* Hospitals
* Medical stores
* Police stations

---

# 7. USER PROBLEMS

Traditional route selection can make it difficult for users to understand:

* Road surface conditions
* Frequency of road hazards
* Hazard locations
* Availability of emergency-related facilities
* Availability of basic travel facilities

SafeRoute AI attempts to provide this information in a structured route-analysis interface.

---

# 8. CORE USER JOURNEY

The primary user flow is:

```text
Open SafeRoute AI
        ↓
Enter Source
        ↓
Enter Destination
        ↓
Request Routes
        ↓
Routing Provider Generates Candidate Routes
        ↓
System Normalizes Routes
        ↓
Up to 4 Routes Displayed
        ↓
Road Images Collected
        ↓
OpenCV Preprocessing
        ↓
YOLO11 Hazard Detection
        ↓
Hazard Aggregation
        ↓
Risk Calculation
        ↓
Nearby Facility Analysis
        ↓
Route Profile Generated
        ↓
LLM Explanation
        ↓
User Inspects Route
```

---

# 9. SYSTEM ARCHITECTURE

The product follows this logical architecture:

```text
┌───────────────────────────────┐
│            USER               │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│          FRONTEND             │
│ Map + Search + Route Cards    │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        BACKEND / API          │
│ Validation + Orchestration    │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       ROUTING ENGINE          │
│ Candidate Route Generation    │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│      IMAGE COLLECTION        │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│          OPENCV               │
│ Image Preprocessing           │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│          YOLO11               │
│ Road Hazard Detection         │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│     HAZARD AGGREGATION        │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       RISK ENGINE             │
│ Deterministic Risk Score      │
└───────────────┬───────────────┘
                │
                ├─────────────────────┐
                ▼                     ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│  FACILITY INTELLIGENCE  │  │    ROUTE PROFILE        │
│ Hospitals etc.          │  │ Combined route data     │
└────────────┬────────────┘  └────────────┬────────────┘
             └───────────────┬────────────┘
                             ▼
                  ┌──────────────────────┐
                  │    LLM EXPLANATION   │
                  │ Grounded Explanation │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │      FRONTEND        │
                  └──────────────────────┘
```

---

# 10. FEATURE REQUIREMENTS

# 10.1 Source and Destination Search

The system MUST provide:

* Source input
* Destination input
* Location search
* Location selection
* Coordinate resolution

### Functional Requirements

FR-001
User MUST be able to enter a source.

FR-002
User MUST be able to enter a destination.

FR-003
System MUST validate that both locations are valid.

FR-004
System MUST convert selected locations into coordinates.

FR-005
System MUST reject invalid locations gracefully.

---

# 10.2 Route Generation

The routing system MUST generate candidate routes.

Maximum supported:

```text
4 routes
```

The system MUST NOT assume that exactly four routes will always exist.

Possible result:

```text
1 route
2 routes
3 routes
4 routes
```

depending on routing-provider availability.

### Route Data

Each route MUST contain:

```text
route_id
distance
duration
geometry
coordinates
segments
```

### Requirements

FR-010
System MUST request candidate routes.

FR-011
System MUST normalize provider-specific route data.

FR-012
Each route MUST have a unique route ID.

FR-013
Routes MUST be independently analyzable.

FR-014
The frontend MUST display available candidate routes.

---

# 10.3 Route Map

The frontend MUST display candidate routes on an interactive map.

Map requirements:

* Source marker
* Destination marker
* Route lines
* Route selection
* Hazard markers
* Facility markers

The user should be able to inspect individual routes.

---

# 10.4 Road Image Collection

The system should collect available road imagery associated with route segments.

Each image should contain metadata where available:

```text
image_id
route_id
segment_id
latitude
longitude
source
timestamp
```

If imagery is unavailable, the system MUST NOT fabricate imagery.

---

# 10.5 Image Processing

OpenCV will be used for image processing.

Possible operations:

* Image validation
* Resizing
* Normalization
* Color conversion
* Noise reduction
* Contrast enhancement
* Image transformation
* Quality assessment

OpenCV is not the primary hazard detector.

---

# 10.6 YOLO11 Hazard Detection

YOLO11 is the primary object-detection model.

The actual detection classes MUST correspond to the training dataset.

Example classes:

```text
pothole
road_crack
damaged_road
obstacle
debris
```

These are examples, not mandatory classes.

### Detection Output

Each detection should include:

```text
image_id
route_id
segment_id
class
confidence
bounding_box
latitude
longitude
model_version
```

---

# 10.7 Hazard Aggregation

The system MUST convert image-level detections into route-level information.

Example:

```text
Image 1 → pothole
Image 2 → pothole
Image 3 → same pothole
```

The system should avoid blindly reporting:

```text
3 potholes
```

if all three detections represent the same physical hazard.

Aggregation should consider:

* Geographic proximity
* Segment
* Image overlap
* Detection location
* Detection confidence

---

# 10.8 Hazard Categories

The system should support configurable hazard classes.

Example:

| Hazard       | Example                   |
| ------------ | ------------------------- |
| Pothole      | Road depression           |
| Road crack   | Visible road cracking     |
| Damaged road | Severely degraded surface |
| Obstacle     | Object blocking road      |
| Debris       | Loose material            |

The actual production classes MUST be determined by the trained dataset.

---

# 11. RISK ENGINE

The Risk Engine calculates the route's road-safety metric.

The risk calculation MUST be deterministic.

The LLM MUST NOT calculate this score.

---

# 11.1 Risk Factors

Potential factors:

* Hazard type
* Hazard severity
* Detection confidence
* Hazard frequency
* Hazard density
* Route exposure
* Segment characteristics

Conceptual model:

```text
Risk =
Σ(
    hazard_weight
    × severity
    × confidence
    × exposure
)
```

The exact mathematical model must be documented separately in:

```text
docs/RISK_ENGINE.md
```

---

# 11.2 Risk Score

The project may normalize the score to:

```text
0–100
```

The system MUST clearly document that this is a project-defined analytical score.

It MUST NOT be represented as an official government safety rating.

---

# 11.3 Risk Score Requirements

FR-050
Same input data MUST produce the same risk result.

FR-051
Risk calculation MUST be reproducible.

FR-052
Risk calculation MUST be testable.

FR-053
Risk score MUST not depend on LLM output.

FR-054
Missing hazard data MUST be handled explicitly.

---

# 12. FACILITY INTELLIGENCE

For every candidate route, the system should analyze nearby facilities.

Required categories:

1. Hospitals
2. Medical stores / pharmacies
3. Restaurants
4. Hotels
5. Petrol pumps / fuel stations
6. Police stations

---

# 12.1 Facility Search Area

Facilities should be searched around the route using a configurable corridor/buffer.

Example configuration:

```text
FACILITY_SEARCH_RADIUS_KM
```

The value should be configurable.

The system should not search the entire city unless explicitly required.

---

# 12.2 Facility Data

Where available:

```text
facility_id
name
category
latitude
longitude
address
phone
distance_from_route
distance_from_nearest_segment
opening_status
source
```

---

# 12.3 Facility Metrics

For each category:

```text
count
nearest_distance
```

Example:

```json
{
  "hospitals": {
    "count": 3,
    "nearest_distance_km": 0.8
  }
}
```

---

# 12.4 Facility Categories

## Emergency Accessibility

* Hospitals
* Medical stores
* Police stations

## Travel Convenience

* Restaurants
* Hotels
* Petrol pumps

These categories MUST remain logically separate from road hazard risk.

---

# 13. ROUTE PROFILE

Each route should have a complete route profile.

Example:

```json
{
  "route_id": "route_1",
  "distance_km": 8.2,
  "duration_minutes": 19,

  "safety": {
    "risk_score": 28,
    "hazards": {
      "potholes": 3,
      "road_cracks": 2,
      "damaged_roads": 1,
      "obstacles": 1,
      "debris": 0
    }
  },

  "facilities": {
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
}
```

---

# 14. ROUTE COMPARISON

The system MUST allow users to inspect multiple routes.

For each route the interface should show:

| Information     | Required |
| --------------- | -------- |
| Distance        | Yes      |
| Duration        | Yes      |
| Risk Score      | Yes      |
| Hazard Count    | Yes      |
| Hazard Types    | Yes      |
| Images Analyzed | Yes      |
| Hospitals       | Yes      |
| Medical Stores  | Yes      |
| Restaurants     | Yes      |
| Hotels          | Yes      |
| Petrol Pumps    | Yes      |
| Police Stations | Yes      |

The interface should present these as factual route attributes rather than hiding the underlying information behind a single AI-generated recommendation.

---

# 15. LLM EXPLANATION ENGINE

The LLM is an explanation layer.

The LLM receives structured data such as:

```text
Route distance
Route duration
Risk metrics
Hazard counts
Facility counts
Nearest facility distances
Analysis status
```

The LLM may generate:

* Route summaries
* Hazard explanations
* Facility summaries
* Route-information explanations
* Answers to user questions about the displayed data

---

# 15.1 LLM Restrictions

The LLM MUST NOT:

* Invent data
* Invent hazards
* Invent facilities
* Invent distances
* Invent route times
* Modify risk scores
* Replace YOLO
* Replace routing
* Make unsupported safety guarantees

---

# 15.2 Grounding

The LLM prompt should explicitly state:

```text
Use only the supplied structured route-analysis data.

Do not invent missing information.

Do not modify numerical values.

If information is unavailable, state that it is unavailable.

Do not claim that a route is completely safe.
```

---

# 16. FRONTEND REQUIREMENTS

The frontend should contain the following major screens/components.

## 16.1 Landing Page

Should communicate:

* SafeRoute AI purpose
* Road safety analysis
* Route comparison
* Hazard detection
* Facility intelligence

---

# 16.2 Route Search

Components:

* Source input
* Destination input
* Search button
* Loading state
* Validation errors

---

# 16.3 Route Map

Should show:

* Source
* Destination
* Candidate routes
* Selected route
* Hazard markers
* Facility markers

---

# 16.4 Route Cards

Each route card should show:

```text
Route 1

8.2 km
19 min

Risk Score
28

Hazards
6

Hospitals
3

Medical Stores
7

Restaurants
15

Hotels
5

Petrol Pumps
2

Police Stations
1
```

---

# 16.5 Route Details

Detailed route view:

```text
Route Overview
      ↓
Map
      ↓
Safety Analysis
      ↓
Hazard Locations
      ↓
Risk Metrics
      ↓
Nearby Facilities
      ↓
AI Explanation
```

---

# 16.6 Map Filters

Users should be able to toggle:

* Hazards
* Hospitals
* Medical stores
* Restaurants
* Hotels
* Petrol pumps
* Police stations

---

# 17. BACKEND REQUIREMENTS

The backend is responsible for:

* Request validation
* Route orchestration
* Data normalization
* Image processing orchestration
* YOLO inference orchestration
* Hazard aggregation
* Risk calculation
* Facility search
* Route profile creation
* LLM orchestration
* Error handling
* Logging
* Authentication if required

---

# 18. API REQUIREMENTS

Suggested API structure:

```text
POST /api/routes

GET /api/routes/{route_id}

POST /api/routes/{route_id}/analyze

GET /api/routes/{route_id}/hazards

GET /api/routes/{route_id}/facilities

GET /api/routes/{route_id}/analysis

POST /api/llm/explanation
```

The exact API structure can be modified if the existing backend architecture requires another design.

---

# 19. DATABASE REQUIREMENTS

Conceptual entities:

```text
users

route_requests

routes

route_segments

road_images

hazards

facilities

route_facilities

route_analysis

model_versions
```

---

# 19.1 Route Request

Possible fields:

```text
request_id
user_id
source
destination
source_latitude
source_longitude
destination_latitude
destination_longitude
created_at
status
```

---

# 19.2 Route

Possible fields:

```text
route_id
request_id
distance
duration
geometry
status
created_at
```

---

# 19.3 Road Image

Possible fields:

```text
image_id
route_id
segment_id
source
latitude
longitude
timestamp
image_path
processing_status
```

---

# 19.4 Hazard

Possible fields:

```text
hazard_id
image_id
route_id
segment_id
hazard_type
confidence
bounding_box
latitude
longitude
model_version
```

---

# 19.5 Facility

Possible fields:

```text
facility_id
name
category
latitude
longitude
address
phone
source
```

---

# 19.6 Route Analysis

Possible fields:

```text
analysis_id
route_id
risk_score
hazard_count
images_analyzed
segments_analyzed
analysis_status
model_version
created_at
```

---

# 20. NON-FUNCTIONAL REQUIREMENTS

# 20.1 Performance

The system should:

* Avoid unnecessary API calls.
* Process images efficiently.
* Batch model inference where appropriate.
* Cache reusable results.
* Avoid duplicate facility queries.
* Avoid unnecessary LLM calls.

---

# 20.2 Scalability

The architecture should allow future support for:

* More users
* More routes
* More images
* More hazard classes
* More facility categories
* Multiple ML models

The initial implementation does not need unnecessary microservices.

---

# 20.3 Reliability

If one optional component fails, the entire system should not necessarily fail.

Example:

```text
Routing       → SUCCESS
YOLO          → SUCCESS
Risk Engine   → SUCCESS
Facilities    → FAILED
LLM           → SUCCESS
```

The user should still receive available route and safety information.

The UI should indicate:

```text
Facility information currently unavailable.
```

---

# 20.4 Security

Requirements:

* Validate inputs
* Protect API keys
* Secure authentication
* Validate image uploads
* Restrict file types
* Restrict file size
* Prevent unauthorized API access
* Apply rate limiting where appropriate
* Avoid exposing backend secrets
* Sanitize user-controlled data

---

# 20.5 Privacy

The system should minimize collection of unnecessary personal information.

Location information should be processed only for required functionality.

Sensitive information should not be unnecessarily stored.

---

# 21. ERROR STATES

The frontend must handle:

### Invalid Source

```text
Please enter a valid source location.
```

### Invalid Destination

```text
Please enter a valid destination.
```

### No Routes

```text
No routes were found for the selected locations.
```

### Fewer Routes

If only two routes are returned:

```text
2 candidate routes available.
```

The system should not create fake Route 3 or Route 4.

### Image Failure

```text
Road imagery is unavailable for part of this route.
```

### YOLO Failure

```text
Road hazard analysis is unavailable for this route.
```

### Facility Failure

```text
Nearby facility information is temporarily unavailable.
```

### LLM Failure

The structured route analysis should remain available even if the LLM fails.

---

# 22. LOADING STATES

The frontend should distinguish processing stages.

Example:

```text
Finding routes...
       ↓
Analyzing road imagery...
       ↓
Detecting road hazards...
       ↓
Calculating route risk...
       ↓
Finding nearby facilities...
       ↓
Preparing route explanation...
```

This helps users understand that analysis may take time.

---

# 23. ANALYSIS STATUS

Each route should have an analysis status.

Possible values:

```text
pending
collecting_images
processing_images
running_detection
aggregating_hazards
calculating_risk
finding_facilities
completed
partial
failed
```

---

# 24. PARTIAL RESULTS

The system should support partial results.

Example:

```text
Route
✓ Distance
✓ Duration
✓ Hazard analysis
✓ Risk score
✗ Facility data
✓ Map
```

The user should still be able to inspect the available information.

---

# 25. MODEL MANAGEMENT

The project must support model versioning.

Example:

```text
Model:
SafeRoute-YOLO11

Version:
v1.0

Dataset:
road-hazards-v1

Confidence Threshold:
configured value
```

Every detection result should be traceable to the model version that generated it.

---

# 26. TRAINING PIPELINE

Training should be separate from application inference.

Recommended structure:

```text
ml/
├── dataset/
├── training/
│   ├── train.py
│   ├── validate.py
│   └── export.py
│
├── models/
└── inference/
    └── detector.py
```

The production application should use a trained model rather than training the model during every user request.

---

# 27. DATASET REQUIREMENTS

The dataset should have:

```text
images/
    train/
    val/
    test/

labels/
    train/
    val/
    test/

data.yaml
```

Dataset documentation should contain:

* Classes
* Number of images
* Annotation format
* Train/validation/test split
* Dataset source
* Licensing information
* Known limitations

Do not claim dataset statistics without verified measurements.

---

# 28. MODEL EVALUATION

The YOLO model should be evaluated using appropriate object-detection metrics.

Potential metrics:

* Precision
* Recall
* mAP
* Confusion matrix
* Per-class performance

The project documentation should distinguish:

```text
Training metrics
```

from:

```text
Real-world road performance
```

High validation performance does not automatically guarantee perfect real-world detection.

---

# 29. OBSERVABILITY

The backend should record useful operational information.

Example:

```text
request_id
route_id
processing_stage
processing_time
model_version
provider_status
error_type
```

Secrets MUST never be logged.

---

# 30. CACHING

Potential cacheable data:

* Route results
* Road images
* YOLO predictions
* Facility searches
* Route analysis
* LLM explanations where appropriate

Cache invalidation should consider:

* Route geometry
* Model version
* Configuration
* Data freshness

---

# 31. FUTURE EXTENSIONS

Potential future features:

* Traffic-aware risk analysis
* Weather-aware route analysis
* Night-time road analysis
* Rain/flood detection
* Road lighting analysis
* Accident-prone-area analysis
* EV charging stations
* Vehicle repair shops
* Tire shops
* Fire stations
* Road construction detection
* Historical road-condition comparison
* User-reported road hazards
* Mobile application

These features are NOT required for Version 1.

---

# 32. VERSION 1 MVP

The first complete version should contain:

## Input

* Source
* Destination

## Routing

* Candidate route generation
* Up to 4 routes
* Map visualization

## Computer Vision

* Road image processing
* OpenCV preprocessing
* YOLO11 hazard detection

## Safety

* Hazard aggregation
* Deterministic risk score

## Facilities

* Hospitals
* Medical stores
* Restaurants
* Hotels
* Petrol pumps
* Police stations

## AI

* Grounded LLM explanation

## UI

* Route cards
* Route details
* Hazard markers
* Facility markers

---

# 33. MVP USER EXPERIENCE

Example:

User enters:

```text
Source:
Alva's Institute of Engineering and Technology

Destination:
Mangaluru
```

System returns:

```text
4 Candidate Routes
```

Example route information:

```text
Route 1
Distance: 8.2 km
Duration: 19 min
Risk Score: 28

Route 2
Distance: 9.1 km
Duration: 22 min
Risk Score: 19

Route 3
Distance: 10.4 km
Duration: 24 min
Risk Score: 34

Route 4
Distance: 11.2 km
Duration: 27 min
Risk Score: 22
```

The system then displays route-specific:

```text
Hazards
Facilities
Map markers
Risk metrics
AI explanation
```

The numbers above are illustrative only and MUST NOT be presented as actual analysis unless generated by the system.

---

# 34. USER STORIES

## US-001 — Search Route

As a user,
I want to enter a source and destination,
so that I can view available routes.

Acceptance Criteria:

* Source accepted.
* Destination accepted.
* Invalid locations rejected.
* Routes returned when available.

---

## US-002 — View Multiple Routes

As a user,
I want to see multiple candidate routes,
so that I can inspect their differences.

Acceptance Criteria:

* System supports up to 4 routes.
* Routes are independently identifiable.
* Each route has distance and duration.

---

## US-003 — View Road Hazards

As a user,
I want to see detected road hazards,
so that I can understand road-condition information.

Acceptance Criteria:

* Hazards are associated with routes.
* Hazard types are displayed.
* Confidence is available internally.
* Hazard locations can be visualized when geographic data exists.

---

## US-004 — View Risk Metrics

As a user,
I want to see route-level risk metrics,
so that I can understand the result of the project's hazard analysis.

Acceptance Criteria:

* Risk is calculated deterministically.
* Same inputs produce consistent results.
* Risk calculation is independent of the LLM.

---

## US-005 — View Facilities

As a user,
I want to see nearby facilities,
so that I can understand what services are available along each route.

Acceptance Criteria:

* Required facility categories are supported.
* Count is shown.
* Nearest distance is shown when available.

---

## US-006 — Understand Route Analysis

As a user,
I want an understandable explanation of route information,
so that I do not need to interpret raw technical data.

Acceptance Criteria:

* LLM receives verified structured data.
* Explanation does not invent information.
* Numerical values remain unchanged.

---

# 35. ACCEPTANCE CRITERIA

The product will be considered functionally complete when:

### Routing

* [ ] Source works.
* [ ] Destination works.
* [ ] Routes are generated.
* [ ] Up to 4 routes supported.
* [ ] Fewer than 4 routes handled correctly.
* [ ] Routes displayed on map.

### Computer Vision

* [ ] Images can be processed.
* [ ] OpenCV pipeline works.
* [ ] YOLO11 model loads.
* [ ] Detection results are parsed.
* [ ] Model version is recorded.

### Hazard Analysis

* [ ] Detections associated with routes.
* [ ] Duplicate detections handled.
* [ ] Route-level hazard summary generated.
* [ ] Risk score calculated deterministically.

### Facilities

* [ ] Facility categories supported.
* [ ] Facilities associated with routes.
* [ ] Counts calculated.
* [ ] Nearest distances calculated.

### LLM

* [ ] Structured data passed to LLM.
* [ ] LLM explanation grounded.
* [ ] No fabricated values.
* [ ] LLM failure does not destroy route analysis.

### Frontend

* [ ] Route cards displayed.
* [ ] Map works.
* [ ] Hazard markers work.
* [ ] Facility markers work.
* [ ] Route details work.
* [ ] Loading states work.
* [ ] Error states work.

### Security

* [ ] Secrets externalized.
* [ ] Input validation implemented.
* [ ] API security considered.
* [ ] File validation implemented where uploads exist.

---

# 36. TESTING STRATEGY

## Unit Tests

Test:

* Risk calculations
* Route normalization
* Hazard aggregation
* Facility aggregation
* YOLO result parsing
* Validation

## Integration Tests

Test:

```text
Frontend
    ↓
Backend
    ↓
Routing
    ↓
Analysis
    ↓
Facilities
    ↓
LLM
```

## End-to-End Tests

Test complete journey:

```text
Source
 ↓
Destination
 ↓
Routes
 ↓
Analysis
 ↓
Route Results
```

---

# 37. PERFORMANCE TARGETS

Exact production targets should be established after measuring the system.

The project should monitor:

* Route-generation latency
* Image-processing latency
* YOLO inference time
* Facility-query latency
* LLM latency
* Total analysis time

Optimization should be based on measured bottlenecks rather than assumptions.

---

# 38. DATA QUALITY REQUIREMENTS

The system should distinguish:

```text
Verified
Estimated
Unavailable
```

Where relevant.

Example:

```text
Road hazard:
Detected

Facility:
Provider data

Risk:
Calculated

LLM explanation:
Generated from backend data
```

---

# 39. TRUST AND TRANSPARENCY

SafeRoute AI MUST NOT imply certainty beyond available evidence.

Avoid:

```text
This road is completely safe.
```

Prefer:

```text
Based on the analyzed road imagery, this route had fewer detected hazards.
```

The UI should make clear that:

* Detection depends on available imagery.
* The model can miss hazards.
* Facility data depends on provider availability.
* Risk scores are project-defined analytical metrics.

---

# 40. PRODUCT LIMITATIONS

Known limitations may include:

1. Road imagery may be incomplete.
2. Images may not represent current road conditions.
3. YOLO11 can produce false positives or false negatives.
4. Facility databases may be incomplete.
5. Route providers may return fewer than four routes.
6. Weather and traffic may change road/travel conditions.
7. Risk scores are analytical outputs rather than guarantees.
8. LLM explanations depend on structured backend data.

These limitations should be documented rather than hidden.

---

# 41. SUCCESS CRITERIA

The project succeeds technically when it demonstrates the complete pipeline:

```text
Source + Destination
        ↓
Candidate Routes
        ↓
Road Images
        ↓
OpenCV
        ↓
YOLO11
        ↓
Hazard Detection
        ↓
Risk Engine
        ↓
Facility Intelligence
        ↓
Route Profile
        ↓
Grounded LLM
        ↓
Interactive UI
```

The system should demonstrate that these components work together as one coherent product.

---

# 42. DEVELOPMENT ROADMAP

## Phase 1 — Foundation

* Repository setup
* Frontend setup
* Backend setup
* Database setup
* Environment configuration
* MASTER_RULES.md
* PRD
* Architecture documentation

---

## Phase 2 — Routing

* Source search
* Destination search
* Routing integration
* Route normalization
* Up to 4 candidate routes
* Map rendering

---

## Phase 3 — Image Pipeline

* Image ingestion
* Image validation
* OpenCV preprocessing
* Image metadata
* Image-to-route association

---

## Phase 4 — YOLO11

* Dataset preparation
* Annotation verification
* Training
* Validation
* Model export
* Inference integration
* Model versioning

---

## Phase 5 — Hazard Engine

* Detection parsing
* Duplicate handling
* Geographic association
* Segment aggregation
* Route-level hazard summary

---

## Phase 6 — Risk Engine

* Hazard weighting
* Confidence handling
* Severity
* Exposure
* Normalization
* Testing

---

## Phase 7 — Facility Intelligence

* Facility provider integration
* Route corridor search
* Category classification
* Count calculation
* Nearest-distance calculation

---

## Phase 8 — Route Profile

Combine:

```text
Route
+
Safety
+
Facilities
+
Analysis Status
```

---

## Phase 9 — LLM

* Structured prompt
* Grounding
* Explanation generation
* Missing-data handling
* Hallucination safeguards

---

## Phase 10 — Production Hardening

* Security
* Error handling
* Logging
* Caching
* Performance
* Tests
* Monitoring
* Documentation

---

# 43. DEFINITION OF DONE

SafeRoute AI Version 1 is complete when:

```text
[✓] User can enter source
[✓] User can enter destination
[✓] Routes are generated
[✓] Up to 4 routes supported
[✓] Routes displayed on map
[✓] Road imagery processed
[✓] OpenCV integrated
[✓] YOLO11 integrated
[✓] Hazards detected
[✓] Hazards aggregated
[✓] Risk calculated
[✓] Facilities analyzed
[✓] Route profile generated
[✓] LLM explanation grounded
[✓] Frontend displays results
[✓] Error handling implemented
[✓] Security requirements addressed
[✓] Tests implemented
[✓] Documentation updated
```

---

# 44. MASTER PRODUCT PRINCIPLE

SafeRoute AI follows this fundamental architecture:

```text
ROUTING
    ↓
Candidate routes

OPENCV
    ↓
Image processing

YOLO11
    ↓
Hazard detection

HAZARD ENGINE
    ↓
Hazard aggregation

RISK ENGINE
    ↓
Deterministic risk analysis

FACILITY ENGINE
    ↓
Nearby services

ROUTE PROFILE
    ↓
Verified structured route information

LLM
    ↓
Natural-language explanation

FRONTEND
    ↓
User-facing visualization
```

No component should silently take over the responsibility of another component.

---

# 45. PRODUCT PRINCIPLE

SafeRoute AI is an **evidence-oriented route analysis system**.

It should not hide the basis of its analysis behind an unexplained AI decision.

The product should expose:

* Route information
* Detected hazards
* Risk metrics
* Facility information
* Data availability
* Analysis limitations

The final interface should help users understand the available information and make their own route choice.

---

# 46. FINAL REQUIREMENT

Any future feature, technology, model, API, database change, or architectural change MUST be evaluated against this PRD and `MASTER_RULES.md`.

If a proposed change:

* Does not support the product purpose,
* Conflicts with the architecture,
* Introduces unnecessary complexity,
* Requires unsupported assumptions,
* Requires fabricated data,
* Or changes a core responsibility,

the change must not be silently implemented.

The project owner must explicitly approve significant scope or architecture changes.

---

# END OF PRD