"""Facility-domain ORM models: Facility, RouteFacility.

Facilities exist independently (one table, categorized); RouteFacility links a
facility to a route only when it falls inside the search corridor.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, JSON, Numeric, String, Text, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import DistanceMetric, FacilityCategory

# JSON column type that works on both SQLite (dev/tests) and PostgreSQL.
JSON_TYPE = JSON


class Facility(Base):
    """Normalized external facility."""

    __tablename__ = "facilities"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(64))
    provider_facility_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    name: Mapped[str] = mapped_column(Text)
    category: Mapped[FacilityCategory] = mapped_column(
        Enum(FacilityCategory, native_enum=False, validate_strings=True)
    )
    latitude: Mapped[float] = mapped_column()
    longitude: Mapped[float] = mapped_column()
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    opening_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # `metadata` is reserved by SQLAlchemy declarative; store provider extras here.
    provider_metadata: Mapped[dict | None] = mapped_column(JSON_TYPE, nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_fac_lat"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_fac_lon"),
    )


class RouteFacility(Base):
    """Route ↔ facility association within the search corridor."""

    __tablename__ = "route_facilities"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routes.id"))
    facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.id"))
    distance_from_route: Mapped[float] = mapped_column(Numeric(6, 3))  # km
    distance_metric: Mapped[DistanceMetric] = mapped_column(
        Enum(DistanceMetric, native_enum=False, validate_strings=True)
    )
    nearest_segment_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("route_segments.id"), nullable=True
    )
    search_radius_km: Mapped[float] = mapped_column(Numeric(5, 2))
    provider: Mapped[str] = mapped_column(String(64))
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    facility: Mapped[Facility] = relationship()
    route: Mapped["Route"] = relationship()  # noqa: F821 - resolved at import time

    __table_args__ = (UniqueConstraint("route_id", "facility_id", name="uq_route_facility"),)