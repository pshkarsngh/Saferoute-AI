from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
class RiskConfigOut(BaseModel):
    """Risk configuration exposed for traceability (10_RISK_ENGINE.md ?3)."""

    model_config = ConfigDict(extra="forbid")
    risk_engine_version: str
    configuration_version: str
    score_scale: str = "0-100"


class RouteProfileOut(BaseModel):
    """Canonical combined Route Profile (07_API_CONTRACT.md ?10)."""

    model_config = ConfigDict(extra="forbid")
    route_id: str
    risk_score: int | None = Field(default=None, ge=0, le=100)
    hazard_count: int | None = None
    hazard_summary: dict = Field(default_factory=dict)
    images_analyzed: int = 0
    segments_analyzed: int = 0
    facilities: dict = Field(default_factory=dict)
    status: str = "unavailable"
    risk_config: RiskConfigOut | None = None
