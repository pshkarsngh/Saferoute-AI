"""Route-domain ORM models: RouteRequest, Route, RouteSegment."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import RequestStatus, RouteStatus, SegmentStatus

# JSON column type that works on both SQLite (dev/tests) and PostgreSQL.
JSON_TYPE = JSON


class RouteRequest(Base):
    """One user request (source + destination) that yields 0-4 routes."""

    __tablename__ = "route_requests"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, native_enum=False, validate_strings=True), default=RequestStatus.completed
    )
    routing_provider: Mapped[str] = mapped_column(String(64))
    source_latitude: Mapped[float] = mapped_column()
    source_longitude: Mapped[float] = mapped_column()
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_place_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    destination_latitude: Mapped[float] = mapped_column()
    destination_longitude: Mapped[float] = mapped_column()
    destination_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    destination_place_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    routes: Mapped[list["Route"]] = relationship(back_populates="request")

    __table_args__ = (
        CheckConstraint("source_latitude BETWEEN -90 AND 90", name="ck_req_src_lat"),
        CheckConstraint("source_longitude BETWEEN -180 AND 180", name="ck_req_src_lon"),
        CheckConstraint("destination_latitude BETWEEN -90 AND 90", name="ck_req_dst_lat"),
        CheckConstraint("destination_longitude BETWEEN -180 AND 180", name="ck_req_dst_lon"),
    )


class Route(Base):
    """Normalized candidate route (1-4 per request; never padded)."""

    __tablename__ = "routes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("route_requests.id"))
    sequence: Mapped[int] = mapped_column(Integer)
    provider: Mapped[str] = mapped_column(String(64))
    provider_route_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    distance_meters: Mapped[float] = mapped_column()
    duration_seconds: Mapped[int] = mapped_column(Integer)
    geometry: Mapped[dict] = mapped_column(JSON_TYPE)
    status: Mapped[RouteStatus] = mapped_column(
        Enum(RouteStatus, native_enum=False, validate_strings=True), default=RouteStatus.available
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    request: Mapped[RouteRequest] = relationship(back_populates="routes")
    segments: Mapped[list["RouteSegment"]] = relationship(back_populates="route", cascade="all, delete-orphan")
    analysis: Mapped["RouteAnalysis | None"] = relationship(back_populates="route", uselist=False)

    __table_args__ = (UniqueConstraint("request_id", "sequence", name="uq_routes_request_seq"),)


class RouteSegment(Base):
    """Analyzable portion of a route; smallest geographic unit for hazards."""

    __tablename__ = "route_segments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routes.id"))
    sequence: Mapped[int] = mapped_column(Integer)
    geometry: Mapped[dict] = mapped_column(JSON_TYPE)
    start_latitude: Mapped[float] = mapped_column()
    start_longitude: Mapped[float] = mapped_column()
    end_latitude: Mapped[float] = mapped_column()
    end_longitude: Mapped[float] = mapped_column()
    length_meters: Mapped[float | None] = mapped_column(nullable=True)
    status: Mapped[SegmentStatus] = mapped_column(
        Enum(SegmentStatus, native_enum=False, validate_strings=True), default=SegmentStatus.pending
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    route: Mapped[Route] = relationship(back_populates="segments")

    __table_args__ = (
        UniqueConstraint("route_id", "sequence", name="uq_segments_route_seq"),
        CheckConstraint("start_latitude BETWEEN -90 AND 90", name="ck_seg_start_lat"),
        CheckConstraint("start_longitude BETWEEN -180 AND 180", name="ck_seg_start_lon"),
        CheckConstraint("end_latitude BETWEEN -90 AND 90", name="ck_seg_end_lat"),
        CheckConstraint("end_longitude BETWEEN -180 AND 180", name="ck_seg_end_lon"),
    )