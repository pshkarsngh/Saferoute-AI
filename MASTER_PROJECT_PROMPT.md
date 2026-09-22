# MASTER PROJECT PROMPT — SAFEROUTE AI

# SafeRoute AI
## Intelligent Road Safety Navigation System
### Master Project Specification, Engineering Rules & Real-World Operation

---

# 1. DOCUMENT PURPOSE

This document is the highest-level engineering specification for the SafeRoute AI project.

It defines:

- What SafeRoute AI is
- Why it exists
- How the system works
- How the system operates in real-world conditions
- System architecture
- Frontend architecture
- Backend architecture
- Routing
- Road imagery collection
- OpenCV processing
- YOLO11 hazard detection
- Hazard aggregation
- Risk calculation
- Facility intelligence
- Route analysis
- LLM explanation
- Database
- API contracts
- Security
- Privacy
- Authentication
- Monitoring
- Logging
- Testing
- Deployment
- Failure handling
- Offline behavior
- External API failures
- Model failures
- Data quality
- AdMob integration if applicable
- AI coding-agent behavior
- Development workflow
- Production-readiness requirements

This document must be treated as the primary project-level source of truth.

All other project documentation must remain consistent with this document.

---

# 2. CORE PROJECT IDEA

SafeRoute AI is an intelligent navigation and road-safety analysis platform.

The system does NOT simply find the shortest route.

Instead, it:

1. Accepts a source and destination.
2. Generates multiple candidate routes.
3. Collects or accesses road imagery associated with those routes.
4. Uses OpenCV for image preprocessing and computer-vision operations.
5. Uses YOLO11 to detect road hazards.
6. Aggregates hazard detections.
7. Calculates a deterministic project-specific road-risk score.
8. Finds nearby facilities along each route.
9. Separates emergency accessibility from travel convenience.
10. Builds a structured route profile.
11. Uses an LLM only to explain verified structured information.
12. Presents the evidence clearly to the user.
13. Allows the user to make their own route decision.

The system must never pretend that an AI model can guarantee road safety.

---

# 3. REAL-WORLD PURPOSE

The real-world problem is:

Traditional navigation systems primarily optimize for:

- distance
- estimated travel time
- traffic
- basic road routing

However, a route that is short or fast may contain:

- potholes
- road cracks
- damaged road surfaces
- debris
- obstacles
- construction-related hazards
- poor road conditions
- other detectable hazards

A route may also differ in accessibility to:

- hospitals
- medical stores
- police stations
- petrol pumps
- hotels
- restaurants

SafeRoute AI adds a road-safety intelligence layer to conventional route planning.

---

# 4. IMPORTANT SYSTEM PRINCIPLE

SafeRoute AI is NOT:

- a replacement for Google Maps
- a replacement for professional navigation systems
- an official road-safety authority
- an accident prediction system
- a medical emergency system
- a guaranteed-safe-route system
- a driver-monitoring system
- an autonomous driving system

SafeRoute AI is:

> A decision-support navigation system that analyzes available road imagery and route-related data to provide transparent road-condition and facility information.

---

# 5. REAL-LIFE USER JOURNEY

The real-world workflow must be understood as follows.

## Step 1 — User Opens SafeRoute AI

The user opens the application.

The system initializes:

- frontend
- map provider
- backend connection
- authentication if required
- configuration
- available services

The application must not expose secret API keys to the client.

---

# 6. USER ENTERS SOURCE AND DESTINATION

The user enters:

```text
Source
Destination

Example:

Source:
Alva's Institute of Engineering and Technology

Destination:
Mangaluru Railway Station
```

The frontend sends a route request to the backend.

Example:

```text
POST /api/routes
```

Request:

```json
{
  "source": {
    "latitude": 12.XXXX,
    "longitude": 74.XXXX
  },
  "destination": {
    "latitude": 12.XXXX,
    "longitude": 74.XXXX
  }
}
```

The backend validates:

```text
coordinates
required fields
coordinate ranges
request format
authentication if required
rate limits
```

# 7. ROUTING ENGINE

The backend communicates with the configured routing provider.

The routing engine generates candidate routes.

The system may return:

```text
Route 1
Route 2
Route 3
Route 4
```

The number of routes is dynamic.

DO NOT hard-code:

```text
Route A
Route B
Route C
Route D
```

as permanent routes.

If the routing provider returns:

```text
2 routes
```

show 2.

If it returns:

```text
4 routes
```

show 4.

If it returns:

```text
1 route
```

show 1.

If no route exists:

```text
No route available
```

# 8. ROUTE INFORMATION

Each route should contain structured information such as:

```json
{
  "route_id": "route_1",
  "distance_km": 8.2,
  "duration_minutes": 19,
  "geometry": {},
  "segments": []
}
```

The route geometry must be treated as authoritative routing output.

The AI/LLM must never modify route geometry.

# 9. ROUTE SEGMENTATION

A route should be divided into analyzable segments.

Example:

```text
Route
 |
 +-- Segment 1
 |
 +-- Segment 2
 |
 +-- Segment 3
 |
 +-- Segment 4
 |
 +-- Segment N
```

Segmentation may be based on:

```text
fixed distance
road geometry
road provider segments
image availability
configurable project logic
```

The segmentation strategy must be documented.

Do not silently change segmentation rules.

# 10. ROAD IMAGERY COLLECTION

The system needs road imagery to analyze road conditions.

Possible sources include:

```text
approved street-level imagery providers
project-owned imagery
uploaded road images
authorized datasets
future user-contributed imagery
```

The source must be recorded.

Example:

```json
{
  "image_id": "img_123",
  "source": "approved_provider",
  "route_id": "route_1",
  "segment_id": "segment_4",
  "latitude": 12.123,
  "longitude": 74.123
}
```

# 11. IMPORTANT REAL-WORLD DATA LIMITATION

SafeRoute AI must NEVER assume that imagery exists for every road.

Possible states:

```text
Imagery Available
Imagery Partially Available
Imagery Unavailable
Imagery Collection Failed
```

If imagery is unavailable:

DO NOT say:

```text
No hazards detected.
```

Instead say:

```text
Road imagery unavailable for this section.
```

This distinction is mandatory.

# 12. IMAGE PREPROCESSING

OpenCV is used for computer-vision preprocessing.

Possible operations include:

```text
resizing
normalization
color conversion
brightness adjustment where justified
contrast adjustment where justified
noise reduction
image validation
cropping
format conversion
```

OpenCV itself must NOT be described as the hazard-detection model unless a separate classical computer-vision detector is explicitly implemented.

Correct:

```text
OpenCV → preprocessing
YOLO11 → object detection
```

Incorrect:

```text
OpenCV detects potholes.
```

unless an actual OpenCV-based detection algorithm exists.

# 13. YOLO11 HAZARD DETECTION

YOLO11 is responsible for object detection.

The model detects only classes that actually exist in the trained dataset.

Example classes:

```text
pothole
road_crack
damaged_road
obstacle
debris
```

These are examples.

The actual classes must come from:

```text
data.yaml
```

and the trained dataset.

Never invent classes that do not exist in the model.

# 14. YOLO OUTPUT

Each detection should contain:

```json
{
  "detection_id": "det_123",
  "image_id": "img_123",
  "route_id": "route_1",
  "segment_id": "segment_4",
  "class": "pothole",
  "confidence": 0.91,
  "bbox": {
    "x1": 100,
    "y1": 150,
    "x2": 300,
    "y2": 350
  }
}
```

Where geographic information is available, associate:

```text
latitude
longitude
```

or another reliable spatial reference.

# 15. MODEL CONFIDENCE

YOLO confidence must be retained.

Example:

```text
Pothole
Confidence: 91%
```

The UI should not imply that:

```text
91% confidence = 91% road danger
```

These are different concepts.

Model confidence indicates detection confidence.

Risk is calculated separately.

# 16. MODEL VERSIONING

Every production analysis should be traceable to:

```text
model name
model version
dataset version
confidence threshold
inference configuration
```

Example:

```json
{
  "model": "YOLO11",
  "model_version": "v1.0.0",
  "confidence_threshold": 0.50
}
```

If the model changes, historical results must remain traceable.

# 17. DUPLICATE DETECTION HANDLING

The same physical pothole may appear in multiple images.

Therefore:

```text
Image 1 → Pothole A
Image 2 → Pothole A
Image 3 → Pothole A
```

must not automatically become:

```text
3 potholes
```

The aggregation layer should use appropriate logic such as:

```text
geographic proximity
segment identity
bounding-box/image relationships
spatial clustering
temporal information when available
```

The exact algorithm must be documented.

# 18. HAZARD AGGREGATION

After YOLO detection:

```text
YOLO detections
      ↓
Validation
      ↓
Duplicate handling
      ↓
Spatial aggregation
      ↓
Hazard summary
```

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

# 19. RISK ENGINE

The risk engine must be deterministic.

The LLM must NOT calculate the final risk score.

Example conceptual formula:

```text
Risk =
Σ(
  hazard_weight
  × confidence
  × severity
  × exposure
)
```

The result may be normalized to:

```text
0–100
```

Example:

```text
Risk Score: 28 / 100
```

This is a project-specific metric.

It must NOT be presented as:

```text
Official government safety score
```

or:

```text
Universal safety standard
```

unless such certification actually exists.

# 20. RISK SCORE EXPLANATION

The system should be able to explain the score using its underlying components.

Example:

```text
Risk Score: 28 / 100

Detected hazards:
- 3 potholes
- 2 road cracks
- 1 damaged-road section

Analyzed imagery:
15 images

Analyzed segments:
24
```

The UI should make it possible to understand where the score came from.

# 21. SAFETY LANGUAGE

Never use:

```text
Completely Safe
100% Safe
Accident Proof
Guaranteed Safe
Zero Accident Risk
Perfect Route
Safest Route
```

unless the statement is explicitly justified by a valid external standard and the exact meaning is documented.

Prefer:

```text
Calculated Risk Score: 28/100
```

and:

```text
No hazards were detected in the analyzed imagery.
```

# 22. FACILITY INTELLIGENCE

SafeRoute AI separately identifies nearby facilities.

Categories:

```text
Emergency Accessibility
-----------------------
Hospitals
Medical Stores
Police Stations

Travel Convenience
------------------
Petrol Pumps
Restaurants
Hotels
```

These categories must remain separate from road safety.

# 23. FACILITY SEARCH

Facility search should be performed around the route corridor.

Do NOT search an entire city unless specifically required.

Use a configurable search corridor:

```text
FACILITY_SEARCH_RADIUS_KM
```

or equivalent route-buffer configuration.

# 24. FACILITY DATA

Example:

```json
{
  "facility_id": "facility_123",
  "name": "Example Hospital",
  "category": "hospital",
  "latitude": 12.123,
  "longitude": 74.123,
  "distance_from_route_km": 0.4,
  "address": "Example Address",
  "phone": "XXXXXXXXXX",
  "source": "provider"
}
```

Only display fields actually returned by the provider.

Do not invent:

```text
phone numbers
opening hours
addresses
ratings
availability
```

# 25. FACILITY SUMMARY

Example:

```text
Emergency Accessibility

Hospitals: 3
Nearest: 0.8 km

Medical Stores: 7
Nearest: 0.2 km

Police Stations: 1
Nearest: 1.2 km

Travel convenience:

Restaurants: 15
Hotels: 5
Petrol Pumps: 2
```

# 26. ZERO VS UNAVAILABLE

This distinction is mandatory.

If the provider successfully searched and found zero:

```text
0 hospitals found
```

If the provider failed:

```text
Hospital data unavailable
```

Never convert:

```text
provider failure
```

into:

```text
0 facilities
```

# 27. ROUTE PROFILE

Each candidate route should receive a structured profile.

Example:

```json
{
  "route_id": "route_1",

  "route": {
    "distance_km": 8.2,
    "duration_minutes": 19
  },

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

  "emergency_accessibility": {
    "hospitals": 3,
    "medical_stores": 7,
    "police_stations": 1
  },

  "travel_convenience": {
    "restaurants": 15,
    "hotels": 5,
    "petrol_pumps": 2
  },

  "analysis": {
    "images_analyzed": 15,
    "segments_analyzed": 24
  }
}
```

# 28. IMPORTANT: DO NOT CREATE ONE OPAQUE SCORE

Do not combine:

```text
Road safety
+
Hospital availability
+
Restaurants
+
Hotels
+
Petrol pumps
```

into one unexplained score.

For example, do NOT create:

```text
Overall AI Score: 94
```

without a transparent, formally documented methodology.

Safety and facilities must remain separate dimensions.

# 29. ROUTE COMPARISON

The frontend may show:

```text
Route 1
8.2 km
19 min
Risk: 28/100
Hospitals: 3

Route 2
9.1 km
21 min
Risk: 19/100
Hospitals: 2

Route 3
10.4 km
23 min
Risk: 15/100
Hospitals: 5
```

The system should present the evidence.

The user decides which trade-off matters to them.

Do not create an opaque AI recommendation such as:

```text
AI says Route 3 is the best.
```

unless the project later introduces a documented decision-support methodology and clearly explains it.

# 30. MAP

The map must show:

```text
source
destination
route geometry
all candidate routes
selected route
hazard markers
facility markers
map controls
legend
```

Up to four routes may be displayed.

Routes must remain visually distinguishable.

Do not depend on color alone.

# 31. ROUTE SELECTION

Selecting a route should:

```text
emphasize the selected route
update route details
update hazard information
update facilities
update route metrics
update evidence
```

It must NOT:

```text
change backend data
modify risk scores
hide evidence
modify YOLO results
```

# 32. HAZARD MARKERS

Each marker may show:

```text
Hazard Type
Confidence
Location
Route Segment
Associated Image
```

Only show information supported by backend data.

# 33. FACILITY MARKERS

Facility markers should be categorized:

```text
Hospital
Medical Store
Police Station
Petrol Pump
Restaurant
Hotel
```

Category filters should allow the user to show/hide categories.

# 34. LLM ROLE

The LLM is an explanation layer.

The LLM receives structured verified data.

Example input:

```json
{
  "distance_km": 8.2,
  "duration_minutes": 19,
  "risk_score": 28,
  "potholes": 3,
  "road_cracks": 2,
  "hospitals": 3,
  "medical_stores": 7
}
```

The LLM explains it in natural language.

# 35. WHAT THE LLM MUST NEVER DO

The LLM must never:

```text
invent hazards
invent facilities
invent route distances
invent travel time
modify route geometry
change risk score
remove hazards
add hazards
create fake addresses
create fake phone numbers
claim real-time data without evidence
override YOLO
replace the routing engine
replace the risk engine
make unsupported medical claims
guarantee safety
```

# 36. LLM GROUNDING RULE

The LLM must follow:

```text
If data exists → explain it.

If data does not exist → say it is unavailable.

If data conflicts → do not silently choose.

If uncertain → state uncertainty.

Never invent missing information.
```

# 37. AI EXPLANATION EXAMPLE

Good:

```text
This route is 8.2 km with an estimated duration of 19 minutes. The analyzed imagery produced a calculated risk score of 28/100, with 3 pothole detections, 2 road-crack detections, and 1 damaged-road detection. Three hospitals were found within the configured route corridor.
```

Bad:

```text
This is the safest route and you will definitely reach your destination safely.
```

# 38. SYSTEM DATA FLOW

The complete system flow is:

```text
USER
 |
 | Source + Destination
 v
FRONTEND
 |
 v
API GATEWAY / BACKEND
 |
 +--------------------+
 |                    |
 v                    v
ROUTING ENGINE      VALIDATION
 |
 v
CANDIDATE ROUTES
 |
 v
ROUTE SEGMENTATION
 |
 v
ROAD IMAGERY
 |
 v
IMAGE VALIDATION
 |
 v
OPENCV PREPROCESSING
 |
 v
YOLO11
 |
 v
HAZARD DETECTION
 |
 v
DUPLICATE / SPATIAL AGGREGATION
 |
 v
RISK ENGINE
 |
 +-----------------------------+
 |                             |
 v                             v
FACILITY INTELLIGENCE       ROUTE METRICS
 |
 v
ROUTE PROFILE
 |
 v
LLM EXPLANATION
 |
 v
FRONTEND
 |
 +----------------------+
 |                      |
 v                      v
MAP                  ROUTE DETAILS
 |
 v
USER DECISION
```

# 39. DATABASE ARCHITECTURE

Recommended logical entities:

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
llm_explanations
audit_logs
```

# 40. DATABASE RELATIONSHIP

```text
USER
 |
 v
ROUTE_REQUEST
 |
 v
ROUTE
 |
 v
ROUTE_SEGMENT
 |
 v
ROAD_IMAGE
 |
 v
HAZARD
```

And:

```text
ROUTE
 |
 +---- FACILITY
 |
 +---- ROUTE_FACILITY
 |
 v
ROUTE_ANALYSIS
```

Model information:

```text
MODEL_VERSION
```

LLM:

```text
LLM_EXPLANATION
```

# 41. API ARCHITECTURE

Suggested endpoints:

```text
POST /api/routes
GET /api/routes/{route_id}

POST /api/routes/{route_id}/analyze

GET /api/routes/{route_id}/hazards

GET /api/routes/{route_id}/facilities

GET /api/routes/{route_id}/analysis

POST /api/llm/explanation
```

Additional endpoints may be created only when justified by the architecture.

Do not create APIs simply to increase endpoint count.

# 42. API CONTRACT RULE

Frontend must not directly communicate with:

```text
YOLO provider
Routing provider
Facility provider
LLM provider
```

unless the architecture explicitly requires a safe client-side SDK.

Prefer:

```text
Frontend
 ↓
Backend API
 ↓
External Providers
```

# 43. EXTERNAL SERVICES

Possible external services:

```text
Routing provider
Map provider
Road imagery provider
Facility/place provider
LLM provider
Authentication provider
Cloud storage
Database
```

Each external service must have:

```text
documented purpose
API contract
authentication method
rate limits
failure behavior
timeout
retry policy
fallback behavior
cost consideration
privacy consideration
```

Do not hard-code provider assumptions.

# 44. SECURITY

Security must cover:

```text
authentication
authorization
input validation
output validation
API security
secret management
rate limiting
CORS
CSRF where applicable
XSS protection
SQL injection protection
command injection prevention
file upload validation
image validation
prompt injection protection
LLM output sanitization
dependency security
logging security
database security
encryption
secure headers
```

# 45. SECRET MANAGEMENT

Never commit:

```text
API keys
LLM keys
Map keys
Database passwords
JWT secrets
Cloud credentials
Service-account credentials
```

Use:

```text
.env
secret manager
deployment platform secrets
```

Never put real secrets in:

```text
frontend source code
README
GitHub
screenshots
documentation
test fixtures
```

# 46. IMAGE UPLOAD SECURITY

If users can upload images:

Validate:

```text
MIME type
extension
file size
dimensions
encoding
malformed files
```

Reject:

```text
executable files
suspicious content
unsupported formats
oversized uploads
```

Do not trust client-provided MIME types alone.

# 47. LLM SECURITY

Treat all external text as untrusted.

This includes:

```text
facility names
facility descriptions
user text
route metadata
uploaded content
provider descriptions
```

Prevent prompt injection.

Do not allow external content to redefine system instructions.

# 48. ERROR HANDLING

Every subsystem must have explicit failure states.

Example:

```text
Route Generation
├── SUCCESS
├── EMPTY
├── FAILED
└── TIMEOUT

Road Imagery
├── AVAILABLE
├── PARTIAL
├── UNAVAILABLE
└── FAILED

YOLO Analysis
├── NOT_STARTED
├── PROCESSING
├── COMPLETED
├── PARTIAL
└── FAILED

Facilities
├── AVAILABLE
├── EMPTY
├── UNAVAILABLE
└── FAILED

LLM
├── NOT_REQUESTED
├── PROCESSING
├── COMPLETED
└── FAILED
```

# 49. PARTIAL RESULTS

SafeRoute AI must support partial success.

Example:

```text
Route generation: SUCCESS
Road imagery: SUCCESS
YOLO analysis: SUCCESS
Risk calculation: SUCCESS
Facilities: FAILED
LLM: SUCCESS
```

The frontend should still display:

```text
Route
Safety analysis
Hazards
Risk score
```

and clearly say:

```text
Facility data unavailable.
```

Do not destroy the entire result.

# 50. ASYNCHRONOUS ANALYSIS

If route analysis takes time, use asynchronous processing.

Example:

```text
Request Route
      ↓
Routes Generated
      ↓
Analysis Job Created
      ↓
Image Processing
      ↓
YOLO
      ↓
Risk Engine
      ↓
Facilities
      ↓
LLM
      ↓
Completed
```

Possible states:

```text
NOT_STARTED
QUEUED
PROCESSING
PARTIAL
COMPLETED
FAILED
```

# 51. FRONTEND ANALYSIS PROGRESS

Show real stages.

Example:

```text
✓ Route generated

✓ Road imagery collected

● Hazard detection

○ Risk calculation

○ Facility analysis

○ AI explanation
```

Do NOT display fake:

```text
87%
88%
89%
90%
```

unless the backend actually reports meaningful progress.

# 52. CACHING

Caching may be used for:

```text
route results
road imagery
facility data
model metadata
repeated analysis
```

Caching must consider:

```text
freshness
provider terms
privacy
location sensitivity
invalidation
storage limits
```

Do not cache sensitive user data indefinitely.

# 53. PERFORMANCE

Optimize:

```text
route geometry
map rendering
marker rendering
image loading
YOLO inference
database queries
API calls
facility queries
LLM requests
```

Use:

```text
lazy loading
batching
caching
pagination where appropriate
marker clustering
image optimization
background processing
```

Only introduce optimization when supported by actual bottlenecks.

# 54. MODEL PERFORMANCE

YOLO11 evaluation must include appropriate ML metrics.

Depending on the project:

```text
Precision
Recall
mAP
F1
Confusion Matrix
Per-class performance
```

Do not claim that model performance is sufficient merely because training completed.

# 55. DATASET MANAGEMENT

Dataset must have:

```text
images/
labels/
train/
val/
test/
data.yaml
```

Dataset documentation must record:

```text
source
license
classes
annotation methodology
split methodology
preprocessing
augmentation
version
limitations
```

Avoid train/test leakage.

# 56. DATA QUALITY

Road imagery may vary due to:

```text
weather
lighting
camera quality
motion blur
occlusion
road type
geographic region
image age
```

These limitations must be documented.

# 57. REAL-WORLD TEMPORAL LIMITATION

A road image may not represent current road conditions.

Therefore the system should preserve:

```text
image timestamp
source
collection date
```

when available.

If imagery is old:

```text
Do not present it as real-time road condition.
```

# 58. LOCATION ACCURACY

Facility and hazard locations depend on provider/GPS accuracy.

Do not imply centimeter-level precision unless the source actually provides it.

# 59. REAL-LIFE EXAMPLE

Suppose a user wants to travel:

```text
A → B
```

The routing engine returns:

```text
Route 1
Route 2
Route 3
```

The system analyzes imagery.

Results:

```text
Route 1
Risk Score: 28/100
Potholes: 3
Cracks: 2
Hospitals: 3
Petrol Pumps: 2

Route 2
Risk Score: 19/100
Potholes: 1
Cracks: 1
Hospitals: 2
Petrol Pumps: 3

Route 3
Risk Score: 41/100
Potholes: 5
Cracks: 3
Hospitals: 5
Petrol Pumps: 4
```

The application does not automatically declare a universal winner.

Instead, it presents:

```text
Route 1
Route 2
Route 3
```

with their evidence.

A user who prioritizes fewer detected road hazards may consider the risk metric important.

Another user may prioritize:

```text
hospital proximity
petrol availability
shorter duration
shorter distance
```

The system provides the information needed for that decision.

# 60. EMERGENCY SCENARIO

Suppose a user is traveling and wants emergency accessibility information.

The system may show:

```text
Hospitals: 3
Nearest: 0.8 km

Medical stores: 7
Nearest: 0.2 km

Police stations: 1
Nearest: 1.2 km
```

However:

The system must not claim:

```text
Hospital is definitely open
```

unless current opening information is reliably available.

It must not claim:

```text
Emergency response guaranteed
```

# 61. OFFLINE / NETWORK FAILURE

If internet connectivity fails:

The app should gracefully handle:

```text
Unable to retrieve route.
```

Previously cached data may be shown if appropriate and clearly labeled as cached.

Do not display stale data as live.

# 62. PROVIDER FAILURE

If routing provider fails:

```text
Route generation unavailable.
```

If facility provider fails:

```text
Facility information unavailable.
```

If LLM fails:

```text
AI explanation unavailable.
```

But structured route analysis should remain available when possible.

# 63. OBSERVABILITY

Production monitoring should include:

```text
API latency
API error rate
route generation failures
image processing failures
YOLO inference failures
facility provider failures
LLM failures
database failures
queue latency
model inference latency
cache hit rate
```

Do not log sensitive information unnecessarily.

# 64. LOGGING

Logs should contain structured information such as:

```text
request_id
route_id
timestamp
service
operation
status
latency
error_code
```

Do not log:

```text
passwords
API keys
access tokens
unnecessary personal data
```

# 65. AUDITABILITY

Important operations should be traceable.

For example:

```text
route_request
model_version
analysis_timestamp
risk_engine_version
facility_provider
LLM model/version
```

This helps reproduce results.

# 66. REPRODUCIBILITY

For a route analysis, preserve enough metadata to understand:

```text
Which route was analyzed?
Which imagery?
Which model?
Which model version?
Which threshold?
Which risk configuration?
Which facility provider?
Which analysis version?
```

# 67. TESTING

Testing must include:

```text
Unit tests

Test:

risk calculation
hazard aggregation
distance calculations
route parsing
facility categorization
validation
state transitions

Integration tests

Test:

Frontend → Backend
Backend → Routing
Backend → Imagery
Backend → YOLO
Backend → Facility provider
Backend → LLM
Backend → Database

End-to-end tests

Test:

Enter locations
→ generate routes
→ analyze route
→ display hazards
→ display facilities
→ display AI explanation
```

# 68. FAILURE TESTING

Explicitly test:

```text
routing timeout
imagery unavailable
YOLO failure
database failure
facility provider failure
LLM timeout
invalid image
invalid coordinates
empty route
zero hazards
zero facilities
partial analysis
network disconnect
```

# 69. SECURITY TESTING

Test:

```text
XSS
SQL injection
CSRF where applicable
authentication bypass
authorization bypass
file upload abuse
prompt injection
malicious LLM output
rate-limit bypass
API abuse
secret exposure
```

# 70. FRONTEND DESIGN PRINCIPLES

The interface should be:

```text
professional
clean
modern
trustworthy
data-driven
accessible
responsive
fast
understandable
```

Avoid:

```text
excessive gradients
unnecessary animations
fake AI effects
3D decoration
gaming UI
crypto-style UI
excessive glassmorphism
clutter
tiny text
```

# 71. MAIN FRONTEND FLOW

```text
Landing / Home
      ↓
Source + Destination
      ↓
Generate Routes
      ↓
Route Comparison
      ↓
Select Route
      ↓
Analyze
      ↓
Safety Dashboard
      ↓
Hazard Evidence
      ↓
Facility Analysis
      ↓
AI Explanation
```

# 72. MAIN UI COMPONENTS

Recommended components:

```text
AppShell
Header
Footer

RouteSearch
LocationInput

MapView
RouteLayer
RouteCard
RouteList
RouteComparison

RiskScore
HazardSummary
HazardMarker
HazardDetails

FacilityFilter
FacilityMarker
FacilityCard
FacilitySummary

AnalysisStatus

LoadingState
EmptyState
ErrorState
UnavailableState
PartialState

AIExplanation

Modal
Drawer
Toast
```

Reuse components.

Do not duplicate UI logic.

# 73. RESPONSIVE DESIGN

```text
Desktop:

Map
+
Route panel

Tablet:

Map
+
Route information

Mobile:

Map
↓
Route cards
↓
Bottom sheet / drawer
```

All functionality must remain accessible on mobile.

# 74. ACCESSIBILITY

Support:

```text
keyboard navigation
semantic HTML
visible focus
accessible labels
ARIA where needed
sufficient contrast
non-color-only information
touch-friendly controls
reduced motion
```

# 75. ROUTE CARD

Each route card may show:

```text
Route 1

8.2 km
19 min

Risk Score
28/100

Hazards
6

Hospitals
3

Medical Stores
7
```

The exact information should depend on API availability.

Do not display fake values.

# 76. MAP INFORMATION HIERARCHY

Map should prioritize:

```text
Route
Source/destination
Selected route
Hazards
Facilities
```

Do not allow decorative UI to overpower the actual navigation information.

# 77. AI EXPLANATION UI

Label it clearly:

```text
AI Route Explanation
```

or:

```text
AI Analysis
```

The user should understand that this is generated text.

The structured data remains authoritative.

# 78. AD MOB

If the application includes AdMob:

AdMob must remain independent from:

```text
Routing
YOLO11
OpenCV
Risk Engine
Facility Intelligence
LLM
```

Ads must never:

```text
cover hazards
cover emergency facilities
cover route controls
block navigation
modify risk
modify routes
modify facility results
```

Ads are secondary to core functionality.

# 79. MONETIZATION PRINCIPLE

The application must never alter analytical results based on advertisers.

The same route analysis must be produced regardless of:

```text
advertiser
ad impression
user interaction with ads
```

# 80. DEPLOYMENT ARCHITECTURE

Production architecture may be:

```text
USER
 |
 v
WEB / MOBILE FRONTEND
 |
 v
API / BACKEND
 |
 +------------------+
 |                  |
 v                  v
DATABASE          CACHE
 |
 v
ASYNC JOB QUEUE
 |
 +------------------------------+
 |                              |
 v                              v
IMAGE PROCESSING             FACILITY SERVICE
 |
 v
YOLO11
 |
 v
RISK ENGINE
 |
 v
LLM SERVICE
```

External:

```text
Routing Provider
Map Provider
Imagery Provider
Facility Provider
LLM Provider
```

# 81. DEVELOPMENT ENVIRONMENTS

Maintain separation:

```text
Development
Staging
Production
```

Never use production secrets in development.

Use test models/test providers where appropriate.

# 82. CI/CD

Production development should include:

```text
lint
format
unit tests
integration tests
security checks
build
deployment
health checks
```

A deployment should not occur if critical tests fail.

# 83. ENVIRONMENT CONFIGURATION

Use environment variables for:

```text
DATABASE_URL
MAP_API_KEY
ROUTING_API_KEY
LLM_API_KEY
IMAGE_PROVIDER_KEY
FACILITY_PROVIDER_KEY
JWT_SECRET
MODEL_PATH
MODEL_VERSION
RISK_CONFIGURATION
```

Do not commit real values.

# 84. CONFIGURATION MANAGEMENT

Risk weights, thresholds, search radius, and provider settings should be configurable.

Avoid scattering magic numbers across source code.

For example:

```text
HAZARD_CONFIDENCE_THRESHOLD
FACILITY_SEARCH_RADIUS_KM
RISK_SCORE_MAX
MAX_CANDIDATE_ROUTES
```

# 85. VERSION CONTROL

Version:

```text
application
API
database schema
YOLO model
dataset
risk engine
configuration
```

Breaking API changes require versioning or migration strategy.

# 86. DATABASE MIGRATIONS

Never manually modify production database schema without a migration process.

Every schema change must be:

```text
versioned
reviewable
repeatable
rollback-aware
```

# 87. PRIVACY

The system may process:

```text
source location
destination location
route information
uploaded images
usage data
```

Collect only what is required.

Define:

```text
retention period
deletion mechanism
access controls
privacy policy
third-party data sharing
```

Do not retain precise location unnecessarily.

# 88. LOCATION PRIVACY

Location data is sensitive.

Do not:

```text
expose private user locations publicly
include exact locations in logs unnecessarily
send location data to unrelated services
retain route history forever without purpose
```

# 89. THIRD-PARTY DATA

Every external provider must be evaluated for:

```text
terms of service
licensing
attribution
commercial usage
API restrictions
caching restrictions
privacy
rate limits
```

Do not scrape providers unless explicitly permitted.

# 90. ROAD IMAGERY LICENSING

Before production deployment, verify that the selected road imagery source permits the intended use.

The system documentation must identify:

```text
imagery provider
license
API restrictions
storage rules
display rules
commercial usage
```

Use:

```text
[DECISION REQUIRED]
```

if the provider has not yet been finalized.

# 91. AI MODEL LICENSING

Verify YOLO11 and all associated model/dataset licenses before commercial deployment.

Record:

```text
model source
license
training dataset source
dataset license
commercial-use restrictions
```

# 92. REAL-WORLD SYSTEM LIMITATIONS

SafeRoute AI cannot guarantee:

```text
current road condition
accident avoidance
absence of hazards
emergency response
facility availability
facility operating status
complete imagery coverage
perfect model detection
```

These limitations must be visible in appropriate product documentation.

# 93. SAFETY DISCLAIMER

The system should communicate appropriately:

```text
SafeRoute AI provides road-condition and route-related information based on available data and analyzed imagery. Results may be incomplete, outdated, or affected by model and data limitations. Users remain responsible for following traffic laws and exercising appropriate judgment.
```

Do not make the disclaimer excessively prominent to the point of destroying usability, but do not hide important limitations.

# 94. NO FABRICATION RULE

The entire project must follow:

```text
NO FAKE DATA
NO FAKE API RESPONSES
NO FAKE HAZARDS
NO FAKE FACILITIES
NO FAKE ROUTES
NO FAKE MODEL RESULTS
NO FAKE AI EXPLANATIONS
```

During development, mock data may be used only when explicitly marked:

```text
MOCK
DEMO
TEST
```

and must never silently reach production.

# 95. REAL DATA VS MOCK DATA

Development:

```text
Mock routing
Mock facilities
Mock YOLO
```

may be used for UI development.

But production configuration must use real services.

The application should make the boundary obvious.

# 96. AI CODING AGENT RULES

Any AI coding agent working on SafeRoute AI must:

```text
Read MASTER_RULES.md.
Read the relevant specification.
Understand the existing repository.
Inspect existing code before modifying it.
Identify dependencies.
Make the smallest correct change.
Preserve existing functionality.
Never rewrite the project unnecessarily.
Never invent missing requirements.
Use [DECISION REQUIRED] where necessary.
Never invent API responses.
Never invent model classes.
Never invent facility data.
Never expose secrets.
Run relevant tests.
Report what changed.
Report verification.
Report remaining issues.
```

# 97. AI AGENT MUST NOT

Do not:

```text
rewrite entire frontend
rewrite entire backend
change framework without approval
replace database without approval
replace routing provider without approval
replace YOLO without approval
replace OpenCV without approval
add unnecessary dependencies
create fake APIs
create fake AI outputs
create fake data
remove existing functionality
modify unrelated files
```

# 98. CHANGE IMPACT RULE

Before changing a component, determine whether the change affects:

```text
API
Database
ML pipeline
Risk Engine
UI
Security
Deployment
Documentation
Testing
```

If yes, update the relevant documentation.

# 99. DOCUMENTATION HIERARCHY

Recommended documentation:

```text
MASTER_RULES.md

01_PRD.md
02_TRD.md
03_ARCHITECTURE.md
04_DATA_MODEL.md
05_DATA_SOURCES.md
06_AI_SOURCES.md
07_API_CONTRACT.md
08_UI_SPEC.md
09_ML_SPEC.md
10_RISK_ENGINE.md
11_FACILITY_SPEC.md
12_LLM_SPEC.md
13_SECURITY.md
14_TESTING.md
15_DEPLOYMENT.md
16_MONITORING.md
17_DEVELOPMENT_ROADMAP.md
18_ADMOB_SPEC.md
19_REAL_WORLD_OPERATION.md
20_LIMITATIONS_AND_ASSUMPTIONS.md
```

# 100. DOCUMENT AUTHORITY

If two documents conflict:

```text
MASTER_RULES.md
MASTER_PROJECT_PROMPT.md
Architecture specification
Domain-specific specification
Implementation documentation
```

The agent must not silently choose between conflicting requirements.

It must report:

```text
[DECISION REQUIRED]
```

# 101. DEVELOPMENT PHASES

```text
Phase 1 — Requirements

Define:

users
use cases
constraints
providers
data sources
ML dataset
risk methodology

Phase 2 — Architecture

Implement:

frontend
backend
database
API
routing

before adding advanced AI functionality.

Phase 3 — Routing

Implement:

source
destination
candidate routes
map
route cards
route geometry

Phase 4 — Imagery

Implement:

imagery acquisition
validation
storage/reference
metadata

Phase 5 — OpenCV

Implement:

image preprocessing
quality checks
normalization

Phase 6 — YOLO11

Implement:

model loading
inference
confidence threshold
class validation
detection storage
model versioning

Phase 7 — Hazard Aggregation

Implement:

duplicate handling
spatial clustering
hazard summaries

Phase 8 — Risk Engine

Implement:

hazard weights
severity
confidence
exposure
normalization

Document every formula.

Phase 9 — Facilities

Implement:

hospital search
medical store search
police station search
petrol pump search
restaurant search
hotel search

Phase 10 — LLM

Implement:

structured prompt
grounded explanation
validation
safe rendering

Phase 11 — Production Security

Implement:

authentication
authorization
rate limiting
secret management
input validation
security headers
logging
monitoring

Phase 12 — Testing

Implement:

unit
integration
E2E
ML evaluation
security
performance
failure testing

Phase 13 — Deployment

Implement:

development
staging
production
CI/CD
monitoring
backups
rollback
```

# 102. REAL-WORLD REQUEST LIFECYCLE

The complete lifecycle should be:

```text
USER OPENS APP
        ↓
USER ENTERS SOURCE
        ↓
USER ENTERS DESTINATION
        ↓
FRONTEND VALIDATES INPUT
        ↓
BACKEND VALIDATES REQUEST
        ↓
ROUTING PROVIDER
        ↓
CANDIDATE ROUTES
        ↓
ROUTE SEGMENTATION
        ↓
ROAD IMAGERY COLLECTION
        ↓
IMAGE VALIDATION
        ↓
OPENCV PREPROCESSING
        ↓
YOLO11 INFERENCE
        ↓
HAZARD VALIDATION
        ↓
DUPLICATE REMOVAL
        ↓
HAZARD AGGREGATION
        ↓
RISK ENGINE
        ↓
FACILITY SEARCH
        ↓
ROUTE PROFILE
        ↓
LLM EXPLANATION
        ↓
FRONTEND
        ↓
MAP + ROUTES + HAZARDS + FACILITIES
        ↓
USER REVIEWS EVIDENCE
        ↓
USER CHOOSES ROUTE
```

# 103. IMPORTANT REAL-LIFE DIFFERENCE

The application does not need to analyze every road image synchronously every time a user searches.

For production scale, the system may use:

```text
preprocessed imagery
cached results
background analysis
existing road-segment analysis
incremental updates
```

Example:

```text
User searches Route A
        ↓
Backend checks cache
        ↓
Existing recent analysis found
        ↓
Reuse analysis if valid
```

If data is stale:

```text
Existing analysis
        ↓
Refresh required
        ↓
Background re-analysis
```

This can reduce:

```text
latency
API cost
compute cost
unnecessary YOLO inference
```

# 104. SCALABILITY

The architecture should support:

```text
10 users
100 users
1,000 users
10,000+ users
```

without requiring a complete rewrite.

Use scalable components such as:

```text
stateless API
database
cache
queue
worker
object storage
model inference service
```

when justified.

# 105. ML WORKER ARCHITECTURE

YOLO inference may be separated into a worker:

```text
API
 |
 v
JOB QUEUE
 |
 v
ML WORKER
 |
 v
YOLO11
 |
 v
RESULT DATABASE
```

This prevents long-running inference from blocking normal API requests.

# 106. COST CONTROL

Track costs for:

```text
routing API
map API
imagery API
facility API
LLM
GPU/CPU inference
storage
database
hosting
```

Use:

```text
caching
batching
rate limiting
request deduplication
model optimization
```

where appropriate.

# 107. RATE LIMITING

Apply rate limits to expensive operations:

```text
route generation
image analysis
YOLO inference
LLM explanation
facility search
```

Do not allow unlimited requests from one client.

# 108. ABUSE PREVENTION

Prevent:

```text
route API abuse
image upload abuse
LLM spam
resource exhaustion
malicious files
automated scraping
```

# 109. HEALTH CHECKS

Production services should expose appropriate health information.

Example:

```text
GET /health
```

and potentially:

```text
GET /ready
```

Health checks should verify necessary dependencies appropriately without exposing sensitive details.

# 110. BACKUP AND RECOVERY

Production must define:

```text
database backup
backup frequency
retention
restore procedure
disaster recovery
rollback
```

# 111. MODEL ROLLBACK

If a new YOLO model performs poorly:

```text
Model v2
 ↓
Problem detected
 ↓
Rollback
 ↓
Model v1
```

Model deployment must be versioned.

# 112. RISK ENGINE VERSIONING

Risk calculations should also be versioned.

Example:

```text
risk_engine_version: 1.0
```

If weights change:

```text
risk_engine_version: 1.1
```

Historical results should remain traceable.

# 113. AI EXPLANATION VERSIONING

Record:

```text
LLM provider
model
prompt version
input data version
timestamp
```

where appropriate.

# 114. USER FEEDBACK

Future versions may allow users to report:

```text
incorrect hazard
missing hazard
incorrect facility
outdated road condition
```

User feedback must not automatically overwrite verified data.

It should enter a review/update workflow.

# 115. FUTURE FEATURES

Possible future extensions:

```text
real-time traffic
weather
road closure information
user road reports
temporal road-condition tracking
severity classification
night-time road analysis
rain/flood detection
construction detection
accident hotspot analysis
historical road-condition trends
mobile application
offline maps
voice interface
```

Do not implement future features unless they are included in the current project scope.

# 116. PROJECT SCOPE CONTROL

When implementing a feature, ask:

```text
Is this required by the current specification?
```

If no:

```text
Do not implement automatically.

Create a future-feature note instead.
```

# 117. DEFINITION OF DONE

A feature is complete only when:

```text
implementation exists
requirements are satisfied
relevant tests pass
error handling exists
security implications are handled
UI states are handled
documentation is updated
no fake data is used
no existing functionality is broken
```

# 118. FINAL PRODUCTION CHECKLIST

Before calling SafeRoute AI production-ready:

```text
Product

[ ] Source/destination works
[ ] Candidate routes work
[ ] Map works
[ ] Route selection works

Computer Vision

[ ] Imagery pipeline works
[ ] OpenCV preprocessing works
[ ] YOLO11 works
[ ] Model versioning exists
[ ] Dataset documented

Safety

[ ] Hazard aggregation works
[ ] Risk formula documented
[ ] Risk score reproducible
[ ] No guaranteed-safety claims

Facilities

[ ] Facility search works
[ ] Categories separated
[ ] Zero/unavailable distinction works

AI

[ ] LLM grounded
[ ] No hallucinated data
[ ] Output validated
[ ] Prompt injection considered

Security

[ ] Secrets protected
[ ] Authentication implemented where required
[ ] Authorization implemented
[ ] Rate limiting
[ ] Input validation
[ ] Upload security
[ ] XSS protection
[ ] Secure headers

Performance

[ ] API optimized
[ ] Map optimized
[ ] ML inference optimized
[ ] Caching considered
[ ] Async processing implemented where needed

Reliability

[ ] Partial failures supported
[ ] Provider failures handled
[ ] Timeouts handled
[ ] Retry policies implemented
[ ] Monitoring exists

Deployment

[ ] Development environment
[ ] Staging environment
[ ] Production environment
[ ] CI/CD
[ ] Database migration
[ ] Backups
[ ] Rollback strategy

Documentation

[ ] Architecture
[ ] API
[ ] Database
[ ] ML
[ ] Risk engine
[ ] Security
[ ] Testing
[ ] Deployment
[ ] Monitoring
[ ] Real-world operation
[ ] Limitations
```

# 119. FINAL ENGINEERING PRINCIPLE

SafeRoute AI must be built as:

```text
A REAL SOFTWARE SYSTEM
+
A REAL COMPUTER-VISION PIPELINE
+
A REAL MACHINE-LEARNING MODEL
+
A DETERMINISTIC RISK ENGINE
+
A FACILITY INTELLIGENCE SYSTEM
+
A GROUNDED AI EXPLANATION LAYER
```

Not as:

```text
A UI mockup
+
Fake AI
+
Fake map data
+
Hard-coded routes
+
Random risk scores
```

# 120. MOST IMPORTANT RULE

The system must always preserve this architecture:

```text
ROUTING
→ generates routes

OPEN CV
→ preprocesses imagery

YOLO11
→ detects hazards

HAZARD AGGREGATION
→ converts detections into structured hazard information

RISK ENGINE
→ calculates the project-defined risk metric

FACILITY ENGINE
→ finds nearby facilities

ROUTE PROFILE
→ combines verified structured information

LLM
→ explains the information

FRONTEND
→ presents evidence

USER
→ makes the final route decision
```

No subsystem may silently take responsibility for another subsystem.

# 121. ABSOLUTE RULES

Never:

```text
fabricate data
invent model results
invent routes
invent facilities
claim guaranteed safety
allow the LLM to modify verified results
expose secrets
bypass API contracts
ignore provider failures
convert unavailable into zero
hide partial failures
silently change risk calculations
hard-code candidate routes
hard-code hazard counts
hard-code facility counts
claim imagery is real-time when it is not
use unlicensed external data
introduce unnecessary dependencies
rewrite unrelated code
destroy existing functionality
```

Always:

```text
validate
document
test
version
monitor
secure
preserve traceability
expose uncertainty
distinguish verified data from AI-generated explanation
let the user see the evidence
preserve human decision-making
```

# 122. FINAL SYSTEM PHILOSOPHY

SafeRoute AI should answer:

```text
"What information can we reliably provide about the available routes and their analyzed road conditions?"
```

It should NOT claim:

```text
"Which route is guaranteed to be safe?"
```

The goal is transparent, evidence-based navigation assistance.

The system should make complex information understandable without hiding uncertainty.

The user remains the final decision-maker.

---

### How SafeRoute AI works in real life

```text
                 USER
                   │
                   ▼
        ┌─────────────────────┐
        │ Source + Destination│
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │   ROUTING ENGINE    │
        │ Generate 1–4 routes │
        └──────────┬──────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
    Route 1              Route 2 ...
          │
          ▼
   Route Segmentation
          │
          ▼
    Road Imagery
          │
          ▼
   ┌───────────────┐
   │    OpenCV     │
   │ Preprocessing │
   └───────┬───────┘
           │
           ▼
      ┌─────────┐
      │ YOLO11  │
      │Detection│
      └────┬────┘
           │
           ▼
    Hazard Detections
           │
           ▼
  Duplicate/Aggregation
           │
           ▼
    ┌──────────────┐
    │ RISK ENGINE  │
    │ 0–100 metric │
    └──────┬───────┘
           │
           ├─────────────────┐
           │                 │
           ▼                 ▼
    Facility Engine     Route Metrics
           │                 │
           └────────┬────────┘
                    ▼
             ROUTE PROFILE
                    │
                    ▼
              ┌──────────┐
              │   LLM    │
              │Explain   │
              └────┬─────┘
                   │
                   ▼
          ┌───────────────────┐
          │ FRONTEND / MAP    │
          │                   │
          │ Routes            │
          │ Hazards           │
          │ Risk              │
          │ Hospitals         │
          │ Medical Stores    │
          │ Police Stations   │
          │ Petrol Pumps      │
          │ Restaurants       │
          │ Hotels            │
          │ AI Explanation    │
          └─────────┬─────────┘
                    │
                    ▼
                  USER
             Makes decision
```

---

# END OF MASTER PROJECT PROMPT