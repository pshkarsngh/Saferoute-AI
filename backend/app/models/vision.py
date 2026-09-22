"""Computer-vision domain ORM models: RoadImage, ImageProcessingResult, HazardDetection, Hazard."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, Numeric, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import HazardStatus, ImageQuality, ProcessingStatus


class RoadImage(Base):
    """Source imagery associated with a route segment."""

    __tablename__ = "road_images"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routes.id"))
    segment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("route_segments.id"))
    source: Mapped[str] = mapped_column(String(128))
    source_image_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_reference: Mapped[str] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    format: Mapped[str | None] = mapped_column(String(16), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(nullable=True)
    image_hash: Mapped[str] = mapped_column(String(64))
    license_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    quality_status: Mapped[ImageQuality | None] = mapped_column(
        Enum(ImageQuality, native_enum=False, validate_strings=True), nullable=True
    )
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, native_enum=False, validate_strings=True), default=ProcessingStatus.collected
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ImageProcessingResult(Base):
    """OpenCV preprocessing outcome for one image (preprocessing only, never detection)."""

    __tablename__ = "image_processing_results"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    image_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("road_images.id"))
    preprocessing_version: Mapped[str] = mapped_column(String(32))
    operations: Mapped[list] = mapped_column(JSON)
    input_width: Mapped[int] = mapped_column(Integer)
    input_height: Mapped[int] = mapped_column(Integer)
    output_width: Mapped[int] = mapped_column(Integer)
    output_height: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16))  # succeeded | failed | rejected
    error: Mapped[str | None] = mapped_column(String(128), nullable=True)
    processing_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class HazardDetection(Base):
    """One YOLO11 inference result in one image (NOT necessarily a unique physical hazard)."""

    __tablename__ = "hazard_detections"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    image_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("road_images.id"))
    route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routes.id"))
    segment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("route_segments.id"))
    model_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("model_versions.id"))
    class_id: Mapped[int] = mapped_column(Integer)
    hazard_type: Mapped[str] = mapped_column(String(64))
    confidence: Mapped[float] = mapped_column(Numeric(4, 3))
    bounding_box: Mapped[dict] = mapped_column(JSON)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    hazard_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("hazards.id"), nullable=True)
    inference_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    hazard: Mapped["Hazard | None"] = relationship(back_populates="detections")


class Hazard(Base):
    """Aggregated unique physical hazard (post dedup/clustering)."""

    __tablename__ = "hazards"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routes.id"))
    segment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("route_segments.id"))
    hazard_type: Mapped[str] = mapped_column(String(64))
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    severity: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    confidence_summary: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    detection_count: Mapped[int] = mapped_column(Integer, default=1)
    aggregation_method: Mapped[str] = mapped_column(String(32))
    first_detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[HazardStatus] = mapped_column(
        Enum(HazardStatus, native_enum=False, validate_strings=True), default=HazardStatus.active
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    detections: Mapped[list[HazardDetection]] = relationship(back_populates="hazard")