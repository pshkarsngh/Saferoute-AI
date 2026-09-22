"""SQLAlchemy ORM models for SafeRoute AI.

Mirrors the authoritative schema in `04_DATA_MODEL.md`. Entities are grouped
by domain. Primary keys are UUIDs; geometry is stored as GeoJSON LineString
JSON; timestamps are timezone-aware UTC.
"""

from app.models.analysis import (
    AnalysisJob,
    DatasetVersion,
    ModelVersion,
    RiskAnalysis,
    RouteAnalysis,
)
from app.models.enums import (
    AnalysisStage,
    AnalysisStatus,
    FacilityCategory,
    HazardStatus,
    ImageQuality,
    ImageSourceStatus,
    ModelStatus,
    ProcessingStatus,
    RiskStatus,
    SegmentStatus,
    ValidationStatus,
)
from app.models.facility import Facility, RouteFacility
from app.models.llm import LLMRequest, LLMResponse
from app.models.route import Route, RouteRequest, RouteSegment
from app.models.vision import (
    Hazard,
    HazardDetection,
    ImageProcessingResult,
    RoadImage,
)

__all__ = [
    "AnalysisJob",
    "AnalysisStage",
    "AnalysisStatus",
    "DatasetVersion",
    "Facility",
    "FacilityCategory",
    "Hazard",
    "HazardDetection",
    "HazardStatus",
    "ImageProcessingResult",
    "ImageQuality",
    "ImageSourceStatus",
    "LLMRequest",
    "LLMResponse",
    "ModelStatus",
    "ModelVersion",
    "ProcessingStatus",
    "RiskAnalysis",
    "RiskStatus",
    "RoadImage",
    "Route",
    "RouteAnalysis",
    "RouteFacility",
    "RouteRequest",
    "RouteSegment",
    "SegmentStatus",
    "ValidationStatus",
]