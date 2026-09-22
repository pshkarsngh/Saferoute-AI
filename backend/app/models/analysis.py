"""Analysis-domain ORM models: ModelVersion, DatasetVersion, RiskAnalysis, RouteAnalysis, AnalysisJob, AuditLog."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, Numeric, String, Text, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import (
    AnalysisStatus,
    AuditAction,
    JobStatus,
    LLMStatus,
    ModelStatus,
    RiskStatus,
    FacilityStatus,
)

# JSON column type that works on both SQLite (dev/tests) and PostgreSQL.
JSON_TYPE = JSON


class DatasetVersion(Base):
    """Dataset a model was trained/validated on. Never fabricate counts."""

    __tablename__ = "dataset_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    dataset_name: Mapped[str] = mapped_column(String(128))
    dataset_version: Mapped[str] = mapped_column(String(64))
    source: Mapped[str] = mapped_column(Text)
    license: Mapped[str] = mapped_column(String(128))
    class_count: Mapped[int] = mapped_column()
    class_definition_reference: Mapped[str] = mapped_column(Text)
    train_count: Mapped[int | None] = mapped_column(nullable=True)
    validation_count: Mapped[int | None] = mapped_column(nullable=True)
    test_count: Mapped[int | None] = mapped_column(nullable=True)
    preprocessing_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("dataset_name", "dataset_version", name="uq_dataset_name_version"),)


class ModelVersion(Base):
    """Exact AI model artifact used for inference (traceability)."""

    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    model_name: Mapped[str] = mapped_column(String(128))
    model_version: Mapped[str] = mapped_column(String(64))
    framework: Mapped[str] = mapped_column(String(64))
    model_artifact_reference: Mapped[str] = mapped_column(Text)
    dataset_version_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("dataset_versions.id"), nullable=True)
    confidence_threshold: Mapped[float] = mapped_column(Numeric(4, 3))
    iou_threshold: Mapped[float] = mapped_column(Numeric(4, 3))
    inference_configuration: Mapped[dict | None] = mapped_column(JSON_TYPE, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[ModelStatus] = mapped_column(
        Enum(ModelStatus, native_enum=False, validate_strings=True), default=ModelStatus.draft
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("model_name", "model_version", name="uq_model_name_version"),)


class RiskAnalysis(Base):
    """Deterministic risk calculation results (the authoritative risk metric)."""

    __tablename__ = "risk_analysis"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routes.id"), unique=True)
    risk_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    risk_scale: Mapped[str] = mapped_column(String(16), default="0-100")
    algorithm_version: Mapped[str] = mapped_column(String(16))
    configuration_version: Mapped[str] = mapped_column(String(16))
    hazard_count: Mapped[int] = mapped_column(default=0)
    weighted_components: Mapped[dict | None] = mapped_column(JSON_TYPE, nullable=True)
    exposure_metrics: Mapped[dict | None] = mapped_column(JSON_TYPE, nullable=True)
    status: Mapped[RiskStatus] = mapped_column(
        Enum(RiskStatus, native_enum=False, validate_strings=True), default=RiskStatus.unavailable
    )
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RouteAnalysis(Base):
    """Aggregated status/profile of one route's analysis (partial-failure aware)."""

    __tablename__ = "route_analysis"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routes.id"), unique=True)
    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus, native_enum=False, validate_strings=True), default=AnalysisStatus.pending
    )
    images_analyzed: Mapped[int] = mapped_column(default=0)
    segments_analyzed: Mapped[int] = mapped_column(default=0)
    hazards_detected: Mapped[int] = mapped_column(default=0)
    hazards_aggregated: Mapped[int] = mapped_column(default=0)
    risk_analysis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("risk_analysis.id"), nullable=True)
    facility_status: Mapped[FacilityStatus] = mapped_column(
        Enum(FacilityStatus, native_enum=False, validate_strings=True), default=FacilityStatus.unavailable
    )
    facility_count: Mapped[int] = mapped_column(default=0)
    llm_status: Mapped[LLMStatus] = mapped_column(
        Enum(LLMStatus, native_enum=False, validate_strings=True), default=LLMStatus.unavailable
    )
    llm_response_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("llm_responses.id"), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    route: Mapped["Route"] = relationship(back_populates="analysis")  # noqa: F821
    risk: Mapped[RiskAnalysis | None] = relationship()


class AnalysisJob(Base):
    """Async analysis progress (used when analysis runs as a background job)."""

    __tablename__ = "analysis_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routes.id"))
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, native_enum=False, validate_strings=True), default=JobStatus.queued
    )
    current_stage: Mapped[str | None] = mapped_column(String(32), nullable=True)
    progress: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    """Immutable record of significant events (no PII, no secrets)."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actor: Mapped[str | None] = mapped_column(String(128), nullable=True)
    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction, native_enum=False, validate_strings=True)
    )
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(Text)
    metadata: Mapped[dict | None] = mapped_column(JSON_TYPE, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())