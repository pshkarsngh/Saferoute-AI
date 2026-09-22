from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
class RouteOut(BaseModel):
    """Normalized candidate route (07_API_CONTRACT.md ?7.2)."""

    model_config = ConfigDict(extra="forbid")
    route_id: str
    request_id: str
    sequence: int = Field(ge=0)
    distance_meters: float = Field(gt=0)
    duration_seconds: int = Field(gt=0)
    geometry: dict | None = None
    status: str = "available"


class RouteRequestOut(BaseModel):
    """Response to POST /api/v1/route-requests (07_API_CONTRACT.md ?7.1)."""

    model_config = ConfigDict(extra="forbid")
    request_id: str
    status: str = "completed"
    routes: list[RouteOut] = Field(default_factory=list, max_length=4)
