"""Shared enumerations for SafeRoute AI ORM models (`04_DATA_MODEL.md`)."""

from __future__ import annotations

import enum


class _StrEnum(str, enum.Enum):
    def _generate_next_value_(self, _start, _count, _last_values):  # pragma: no cover
        return self.name


class RequestStatus(_StrEnum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class RouteStatus(_StrEnum):
    available = "available"
    failed = "failed"


class SegmentStatus(_StrEnum):
    pending = "pending"
    collected = "collected"
    processed = "processed"
    failed = "failed"


class ProcessingStatus(_StrEnum):
    collected = "collected"
    validated = "validated"
    invalid = "invalid"
    processed = "processed"
    analyzed = "analyzed"
    failed = "failed"


class ImageQuality(_StrEnum):
    ok = "ok"
    low_quality = "low_quality"
    corrupt = "corrupt"


class ImageSourceStatus(_StrEnum):
    available = "available"
    partial = "partial"
    unavailable = "unavailable"
    failed = "failed"


class HazardStatus(_StrEnum):
    active = "active"
    reviewed = "reviewed"
    dismissed = "dismissed"


class AnalysisStatus(_StrEnum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    partial = "partial"
    failed = "failed"


class RiskStatus(_StrEnum):
    calculated = "calculated"
    unavailable = "unavailable"


class ModelStatus(_StrEnum):
    draft = "draft"
    active = "active"
    retired = "retired"


class FacilityCategory(_StrEnum):
    hospital = "hospital"
    medical_store = "medical_store"
    restaurant = "restaurant"
    hotel = "hotel"
    petrol_pump = "petrol_pump"
    police_station = "police_station"


class DistanceMetric(_StrEnum):
    straight_line = "straight_line"
    driving = "driving"
    to_nearest_segment = "to_nearest_segment"


class FacilityStatus(_StrEnum):
    completed = "completed"
    unavailable = "unavailable"


class LLMStatus(_StrEnum):
    completed = "completed"
    fallback = "fallback"
    failed = "failed"
    unavailable = "unavailable"


class ValidationStatus(_StrEnum):
    valid = "valid"
    needs_review = "needs_review"
    failed = "failed"


class AnalysisStage(_StrEnum):
    route_generation = "ROUTE_GENERATION"
    image_collection = "IMAGE_COLLECTION"
    image_validation = "IMAGE_VALIDATION"
    opencv_preprocessing = "OPENCV_PREPROCESSING"
    yolo_inference = "YOLO_INFERENCE"
    hazard_aggregation = "HAZARD_AGGREGATION"
    risk_calculation = "RISK_CALCULATION"
    facility_analysis = "FACILITY_ANALYSIS"
    route_profile = "ROUTE_PROFILE"
    llm_explanation = "LLM_EXPLANATION"
    completed = "COMPLETED"


class JobStatus(_StrEnum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    partial = "partial"
    failed = "failed"
    cancelled = "cancelled"


class AuditAction(_StrEnum):
    analysis_started = "analysis_started"
    analysis_completed = "analysis_completed"
    analysis_partial = "analysis_partial"
    model_activated = "model_activated"
    model_retired = "model_retired"