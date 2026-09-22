"""LLM-domain ORM models: LLMRequest, LLMResponse.

These persist grounded explanation interactions for audibility. Generated LLM
text never overwrites authoritative values.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import ValidationStatus

# JSON column type that works on both SQLite (dev/tests) and PostgreSQL.
JSON_TYPE = JSON


class LLMRequest(Base):
    """One grounded explanation request tied to a route analysis."""

    __tablename__ = "llm_requests"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    route_analysis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("route_analysis.id"))
    provider: Mapped[str] = mapped_column(String(64), default="openai_compatible")
    model: Mapped[str] = mapped_column(String(128))
    prompt_version: Mapped[str] = mapped_column(String(16))
    input_schema_version: Mapped[str] = mapped_column(String(16), default="v1")
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(16), default="requested")  # requested | completed | failed

    response: Mapped["LLMResponse | None"] = relationship(back_populates="request", uselist=False)


class LLMResponse(Base):
    """Validated explanation response. Generated data — not authoritative."""

    __tablename__ = "llm_responses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    llm_request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("llm_requests.id"))
    response_text: Mapped[str] = mapped_column(Text)
    response_schema_version: Mapped[str] = mapped_column(String(16), default="v1")
    validation_status: Mapped[ValidationStatus] = mapped_column(
        Enum(ValidationStatus, native_enum=False, validate_strings=True), default=ValidationStatus.valid
    )
    is_fallback: Mapped[bool] = mapped_column(default=False)
    token_usage: Mapped[dict | None] = mapped_column(JSON_TYPE, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    request: Mapped[LLMRequest] = relationship(back_populates="response")