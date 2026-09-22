# MASTER RULES — SAFEROUTE AI

Version: 1.0
Project: SafeRoute AI
Project Type: Major College Project
Status: Production-Oriented Development

---

# 1. PURPOSE OF THIS FILE

This file is the MASTER RULEBOOK for the SafeRoute AI project.

Every AI coding agent, developer, automated coding tool, or assistant working
on this repository MUST follow these rules.

These rules define:

- Project scope
- Architecture
- Technology responsibilities
- Development boundaries
- AI/ML responsibilities
- Coding standards
- Security requirements
- Data requirements
- Testing requirements
- Change management
- Prohibited behavior

The agent MUST NOT work outside these rules unless the project owner
explicitly approves the change.

---

# 2. HIGHEST PRIORITY

Always follow this priority order:

1. Correctness
2. MASTER_RULES.md
3. Explicit user requirements
4. Existing project architecture
5. Existing working functionality
6. Security and reliability
7. Maintainability
8. Performance
9. Token/context efficiency
10. Minimal unnecessary changes

Never sacrifice project correctness merely to produce code quickly.

---

# 3. CORE PROJECT DEFINITION

Project Name:

SafeRoute AI — Intelligent Road Safety Navigation System

Core purpose:

SafeRoute AI is a navigation and road-safety analysis system that:

1. Accepts source and destination.
2. Generates candidate routes using a routing provider.
3. Supports up to 4 candidate routes.
4. Collects road/route imagery where available.
5. Uses OpenCV for image preprocessing.
6. Uses YOLO11 for road-hazard detection.
7. Aggregates detected hazards by route/segment.
8. Calculates a deterministic road-risk score.
9. Finds nearby facilities around each route.
10. Creates a structured route profile.
11. Uses an LLM only to explain verified results.
12. Presents the results to the user through the frontend.

The system MUST remain centered around this purpose.

---

# 4. PROJECT BOUNDARY

The following are IN SCOPE:

- Route generation
- Route comparison
- Road hazard detection
- Road image processing
- OpenCV
- YOLO11
- Hazard aggregation
- Risk scoring
- Facility discovery
- Route safety analysis
- Map visualization
- Backend APIs
- Frontend dashboard
- Database
- LLM-based explanation
- Testing
- Logging
- Caching
- Security
- Model versioning

The following are OUT OF SCOPE unless explicitly approved:

- Social media platform
- E-commerce platform
- Payment system
- Chat application unrelated to navigation
- Cryptocurrency
- Blockchain
- Generic AI chatbot
- Facial recognition
- User surveillance
- Unrelated recommendation systems
- Unrelated computer vision features
- Unrelated ML models
- Unrelated microservices
- Features added merely because they are "cool"

If a requested feature does not support the SafeRoute AI objective,
DO NOT implement it without explicit approval.

---

# 5. ARCHITECTURE RULE

The system MUST follow this logical pipeline:

```
USER
  ↓
FRONTEND
  ↓
BACKEND/API
  ↓
ROUTE GENERATION
  ↓
ROUTE NORMALIZATION
  ↓
ROAD IMAGE COLLECTION
  ↓
OPENCV PREPROCESSING
  ↓
YOLO11 DETECTION
  ↓
HAZARD AGGREGATION
  ↓
RISK SCORE ENGINE
  ↓
FACILITY INTELLIGENCE
  ↓
ROUTE PROFILE
  ↓
LLM EXPLANATION
  ↓
FRONTEND
```

Do not bypass major architectural layers without a documented reason.

---

# 6. RESPONSIBILITY OF EACH TECHNOLOGY

## 6.1 Routing Provider

Responsible for:

- Generating routes
- Distance
- Duration
- Route geometry
- Route coordinates
- Route segments

The routing provider generates candidate routes.

SafeRoute AI evaluates them.

Do NOT hard-code Route A, Route B, Route C, or Route D.

Routes must be dynamically represented.

Maximum supported candidate routes:

4

The actual number may be less than 4 if the routing provider returns fewer
valid alternatives.

---

# 7. OPENCV RULES

OpenCV is responsible for image processing and preprocessing.

Allowed responsibilities:

- Image loading
- Image validation
- Resizing
- Normalization
- Color conversion
- Noise reduction
- Contrast enhancement
- Image transformations
- Frame extraction where applicable
- Image quality checks

OpenCV MUST NOT be described as the hazard detection model unless an actual
OpenCV detection algorithm is implemented.

Hazard detection is primarily handled by YOLO11.

---

# 8. YOLO11 RULES

YOLO11 is responsible for object detection of road hazards.

Potential classes may include:

- pothole
- road_crack
- damaged_road
- obstacle
- debris

IMPORTANT:

Only classes actually present in the project's annotated dataset may be used.

Never invent detection classes.

YOLO output MUST contain, where applicable:

- class
- confidence
- bounding box
- image ID
- route ID
- segment ID
- geographic information

Model version MUST be tracked.

Never silently replace the trained model.

---

# 9. DATASET RULES

Training data MUST be separated from production code.

Recommended structure:

```
ml/
├── dataset/
│   ├── images/
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   │
│   ├── labels/
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   │
│   └── data.yaml
│
├── training/
└── inference/
```

Never commit:

- API keys
- passwords
- private credentials
- personal data
- huge generated datasets
- model secrets

unless explicitly required and safely configured.

---

# 10. ROUTE REPRESENTATION

Every route MUST have a unique route ID.

Example:

route_1
route_2
route_3
route_4

The application MUST NOT assume exactly four routes exist.

Each route should contain:

- route_id
- geometry
- coordinates
- distance
- duration
- segments
- analysis status

---

# 11. ROUTE SEGMENTS

Routes should be divided into analyzable segments.

Each segment should have:

- segment_id
- route_id
- geometry
- coordinates
- road images
- detected hazards
- analysis status

Hazards should be associated with the smallest practical geographic unit.

---

# 12. HAZARD AGGREGATION

YOLO detections are image-level results.

They MUST NOT automatically be treated as unique real-world hazards.

The system should consider:

- duplicate detections
- overlapping images
- nearby detections
- segment association
- geographic clustering

Example:

If the same pothole appears in 5 overlapping images,
the system should avoid blindly counting it as 5 separate potholes.

---

# 13. RISK SCORE RULE

The risk score MUST be deterministic.

The LLM MUST NOT calculate the official project risk score.

Conceptually:

```
Risk =
Σ(
    Hazard Weight
    × Severity
    × Confidence
    × Exposure
)
```

The exact formula must be defined in the project's risk-engine documentation.

The score MUST be normalized consistently.

Example:

0–100

IMPORTANT:

The project risk score is a project-defined analytical metric.

It MUST NOT be presented as an official government or universal road-safety
standard.

---

# 14. SAFETY AND FACILITY DATA MUST REMAIN SEPARATE

DO NOT combine all information into one arbitrary score.

Example:

Hospitals
+ Restaurants
+ Hotels
+ Petrol Pumps
+ Police Stations
+ Potholes

MUST NOT simply be added together to create a "Safety Score".

Instead maintain separate dimensions:

## Road Safety

- risk score
- hazards
- hazard density
- severity
- confidence

## Emergency Accessibility

- hospitals
- medical stores
- police stations

## Travel Convenience

- restaurants
- hotels
- petrol pumps

## Route Information

- distance
- duration

---

# 15. FACILITY INTELLIGENCE

For each route, the system may analyze:

- Hospitals
- Medical stores / pharmacies
- Restaurants
- Hotels
- Petrol pumps / fuel stations
- Police stations

Future categories may be added only if they support the project.

Facility searches MUST use a route corridor/buffer.

Do NOT search the entire city unnecessarily.

Each facility should contain, where available:

- facility_id
- name
- category
- latitude
- longitude
- distance from route
- nearest segment
- address
- phone
- opening status
- source

Never fabricate facility information.

---

# 16. LLM RULES

The LLM is an EXPLANATION LAYER.

The LLM MUST NOT become the primary decision engine.

The LLM may:

- Explain route differences
- Summarize hazards
- Explain facility availability
- Convert structured results into natural language
- Answer user questions about verified route data

The LLM MUST NOT:

- Invent hazards
- Invent facilities
- Invent distances
- Invent route data
- Invent risk scores
- Modify the deterministic risk score
- Replace YOLO11
- Replace the routing engine
- Claim a route is completely safe
- Create unsupported facts

The LLM must receive structured backend data.

If data is unavailable:

Say that the data is unavailable.

Never fill missing information with guesses.

---

# 17. FRONTEND RULES

The frontend should provide:

- Source input
- Destination input
- Map
- Candidate routes
- Route cards
- Hazard markers
- Facility markers
- Route details
- Risk information
- Facility information
- LLM explanation

The UI should allow users to inspect each candidate route.

Do not hide important analytical information behind unexplained AI decisions.

---

# 18. ROUTE CARD REQUIREMENTS

Each route card may display:

- Route name/ID
- Distance
- Estimated duration
- Risk score
- Hazard count
- Hazard types
- Images analyzed
- Hospitals
- Medical stores
- Restaurants
- Hotels
- Petrol pumps
- Police stations

Example:

```
Route 1

Distance: 8.2 km
Duration: 19 min
Risk Score: 28

Hazards:
Potholes: 3
Cracks: 2
Obstacles: 1

Nearby:
Hospitals: 3
Medical Stores: 7
Restaurants: 15
Hotels: 5
Petrol Pumps: 2
Police Stations: 1
```

---

# 19. BACKEND API RULES

APIs should be resource-oriented.

Possible endpoints:

```
POST /api/routes
GET  /api/routes/{route_id}
POST /api/routes/{route_id}/analyze
GET  /api/routes/{route_id}/hazards
GET  /api/routes/{route_id}/facilities
GET  /api/routes/{route_id}/analysis
POST /api/llm/explanation
```

Do not create unnecessary endpoints.

Before creating a new endpoint:

1. Check whether an existing endpoint already provides the functionality.
2. Reuse existing structures where possible.
3. Add a new endpoint only when architecturally justified.

---

# 20. DATABASE RULES

Conceptual entities:

```
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

Relationships:

```
USER
  ↓
ROUTE_REQUEST
  ↓
ROUTE
  ↓
ROUTE_SEGMENT
  ↓
ROAD_IMAGE
  ↓
HAZARD

ROUTE
  ↓
FACILITY
  ↓
ROUTE_FACILITY

ROUTE
  ↓
ROUTE_ANALYSIS
```

Use the project's existing database technology if one is already established.

Do not replace the database without explicit approval.

---

# 21. SECURITY RULES

NEVER hard-code:

- API keys
- passwords
- tokens
- database credentials
- private keys

Use environment variables or the project's secure configuration system.

Validate:

- user input
- coordinates
- image type
- image size
- API parameters
- uploaded files

Implement appropriate:

- authentication
- authorization
- rate limiting
- input validation
- error handling

Never expose secrets to frontend code.

---

# 22. ERROR HANDLING

The system MUST gracefully handle:

- Invalid source
- Invalid destination
- No route found
- Routing API failure
- Fewer than 4 routes
- Image unavailable
- Invalid image
- OpenCV failure
- YOLO failure
- Database failure
- Facility API failure
- LLM failure
- Timeout
- Rate limit
- Network failure

Optional components should fail gracefully.

Example:

If facility data is unavailable:

Do NOT invent facilities.

Return:

facility_data_status = unavailable

while preserving available route and safety data.

---

# 23. NO FABRICATION RULE

This is one of the STRICTEST rules.

The AI MUST NEVER fabricate:

- Routes
- Road conditions
- YOLO detections
- Facility counts
- Facility names
- Distances
- Risk scores
- Model accuracy
- Dataset statistics
- API responses
- Test results

If information is unavailable:

State that it is unavailable.

---

# 24. CONFIGURATION RULE

Do not hard-code values that should be configurable.

Examples:

- API URLs
- API keys
- model path
- model version
- confidence threshold
- facility search radius
- risk weights
- image limits
- route limits
- timeout values

Use configuration files or environment variables.

---

# 25. MODEL VERSIONING

Every production inference should be traceable to a model version.

Example:

```
YOLO Model: safroute-yolo11-v1
```

Store:

- model name
- version
- training date
- dataset version
- confidence threshold
- class list

Never silently change the model.

---

# 26. PERFORMANCE RULES

Optimize actual bottlenecks.

Likely bottlenecks:

- image retrieval
- YOLO inference
- facility APIs
- LLM calls
- database queries

Use where appropriate:

- batching
- caching
- image resizing
- duplicate removal
- asynchronous processing
- database indexing

Do NOT introduce unnecessary distributed systems.

---

# 27. MICROSERVICE RULE

DO NOT create microservices simply because the project is described as
"production-level".

Start with a modular architecture.

Introduce:

- message queues
- separate inference services
- distributed workers
- Kubernetes
- microservices

ONLY when there is a demonstrated architectural requirement.

Complexity must be justified.

---

# 28. CODE CHANGE RULE

Before modifying code:

1. Understand the requirement.
2. Inspect the relevant files.
3. Understand existing architecture.
4. Identify dependencies.
5. Plan the smallest correct change.
6. Implement the change.
7. Test the affected functionality.

Do NOT rewrite unrelated files.

---

# 29. EXISTING CODE RULE

Existing working code is presumed intentional.

DO NOT:

- rewrite everything
- change frameworks unnecessarily
- rename files without reason
- replace libraries without reason
- delete working features
- change database technology
- change architecture
- change APIs

unless explicitly approved.

---

# 30. DEPENDENCY RULE

Before adding a dependency:

1. Check whether the functionality already exists.
2. Check whether an existing dependency can perform it.
3. Check whether the dependency is actually required.
4. Prefer stable and maintained packages.
5. Document why the dependency is needed.

Never add packages simply because they are convenient.

---

# 31. TESTING RULE

Important functionality MUST have appropriate tests.

At minimum test:

### Routing

- route generation
- route normalization
- multiple routes
- fewer than 4 routes

### Computer Vision

- image validation
- OpenCV preprocessing
- YOLO output parsing

### Hazard Engine

- aggregation
- duplicate handling
- confidence handling

### Risk Engine

- deterministic calculation
- boundary values
- missing data

### Facilities

- category aggregation
- route distance
- missing provider data

### LLM

- structured input
- grounding
- missing data handling

### API

- valid requests
- invalid requests
- errors
- timeouts

---

# 32. LOGGING RULE

Use structured logs where practical.

Useful fields:

- request_id
- route_id
- segment_id
- model_version
- processing_stage
- duration
- error_type

NEVER log:

- API keys
- passwords
- authentication tokens
- private credentials

---

# 33. CACHE RULE

Caching may be used for:

- route results
- road images
- YOLO detections
- facility results
- route analysis

Cache keys MUST include relevant version/configuration information.

For example:

route geometry
+
image ID
+
model version
+
configuration

must be considered when determining whether cached analysis is valid.

---

# 34. AI AGENT BEHAVIOR

When working on this repository, the AI MUST:

- Think about architecture before coding.
- Inspect relevant files before modifying them.
- Follow MASTER_RULES.md.
- Preserve existing functionality.
- Make minimal targeted changes.
- Explain assumptions when necessary.
- Ask for clarification when requirements conflict.
- Never silently change project direction.
- Never introduce unrelated features.

---

# 35. FORBIDDEN AI BEHAVIOR

The AI MUST NOT:

- Invent requirements.
- Invent APIs.
- Invent data.
- Invent test results.
- Invent model performance.
- Invent dataset statistics.
- Invent route information.
- Add unrelated features.
- Replace architecture without approval.
- Change frameworks without approval.
- Add unnecessary dependencies.
- Delete working functionality.
- Modify unrelated files.
- Expose secrets.
- Guess missing information.
- Pretend an API/model succeeded when it failed.

---

# 36. REQUIREMENT CONFLICT RULE

If the user request conflicts with this architecture:

STOP before implementation.

Determine whether the requested change is:

A. Compatible with the architecture
B. A small architectural extension
C. An architectural change

If C:

Explain:

- current architecture
- requested change
- affected components
- risks
- required modifications

Do not silently make the architectural change.

---

# 37. BEFORE CODING CHECKLIST

Before writing code, verify:

[ ] What exactly is being requested?
[ ] Which existing files are relevant?
[ ] Which architecture component is affected?
[ ] Does the feature belong to SafeRoute AI?
[ ] Is there already an implementation?
[ ] Can existing code be reused?
[ ] Are new dependencies necessary?
[ ] Are APIs affected?
[ ] Is the database affected?
[ ] Is security affected?
[ ] Are tests required?

---

# 38. AFTER CODING CHECKLIST

After implementation:

[ ] Code compiles/runs
[ ] Relevant tests pass
[ ] Existing functionality still works
[ ] No unrelated files changed
[ ] No secrets exposed
[ ] Error handling exists
[ ] API contracts remain valid
[ ] Database changes are valid
[ ] ML model integration is valid
[ ] Risk calculation is deterministic
[ ] Facility data is not fabricated
[ ] LLM receives verified structured data

---

# 39. PROJECT SCOPE GATE

Every new feature MUST pass this question:

"Does this feature directly improve route generation, road-safety analysis,
hazard detection, facility intelligence, route understanding, or the
SafeRoute AI user experience?"

If NO:

Do not implement it without explicit project-owner approval.

---

# 40. CHANGE CONTROL

For significant architectural changes, document:

## Change

What is changing?

## Reason

Why is it required?

## Impact

Which components are affected?

## Alternatives

What alternatives were considered?

## Risks

What could break?

## Approval

Has the project owner approved the change?

---

# 41. DOCUMENTATION RULE

Architecture-changing decisions MUST be documented.

Relevant documentation belongs in:

docs/

Possible files:

```
ARCHITECTURE.md
API.md
DATABASE.md
AI_MODELS.md
ROADMAP.md
```

MASTER_RULES.md should contain rules.

Detailed technical explanations should normally go into docs/.

---

# 42. DEVELOPMENT PHASES

The project should generally progress in this order:

```
PHASE 1    Project foundation
PHASE 2    Routing and up to 4 candidate routes
PHASE 3    Road image pipeline
PHASE 4    OpenCV preprocessing
PHASE 5    YOLO11 dataset/training/inference
PHASE 6    Hazard aggregation
PHASE 7    Risk scoring
PHASE 8    Facility intelligence
PHASE 9    Route profile
PHASE 10   LLM explanation
PHASE 11   Testing
PHASE 12   Security/performance/production hardening
```

Do not skip foundational architecture simply to build UI features.

---

# 43. DEFINITION OF DONE

A feature is NOT complete merely because code exists.

A feature is complete only when:

- Requirement is implemented.
- Architecture is preserved.
- Code is integrated.
- Error handling exists.
- Relevant tests exist/pass.
- Security requirements are satisfied.
- Existing functionality remains intact.
- Documentation is updated when required.
- No fabricated data is used.

---

# 44. FINAL RESPONSE FORMAT FOR AI AGENTS

After completing work, report:

## Changed

- File/component
- What changed

## Reason

- Why it was changed

## Verification

- Tests/build/lint performed
- Result

## Notes

- Important assumptions
- Known limitations

Do not provide unnecessary explanations.

---

# 45. ABSOLUTE PROJECT PRINCIPLE

SafeRoute AI follows this architecture:

ROUTING
generates candidate routes.

OPENCV
prepares and processes images.

YOLO11
detects road hazards.

HAZARD ENGINE
aggregates detections.

RISK ENGINE
calculates deterministic road-risk metrics.

FACILITY ENGINE
finds nearby facilities.

ROUTE PROFILE ENGINE
combines verified structured information.

LLM
explains verified information.

FRONTEND
presents the information to the user.

The AI agent MUST preserve these responsibilities.

---

# 46. FINAL RULE

When uncertain:

DO NOT GUESS.

DO NOT EXPAND THE SCOPE.

DO NOT CHANGE THE ARCHITECTURE.

DO NOT FABRICATE DATA.

DO NOT REWRITE WORKING CODE.

Instead:

1. Inspect.
2. Understand.
3. Follow the architecture.
4. Make the smallest correct change.
5. Verify.
6. Report.

END OF MASTER RULES