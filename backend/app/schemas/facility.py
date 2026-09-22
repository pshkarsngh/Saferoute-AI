from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
class FacilityOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    facility_id: str
    name: str
    category: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    distance_from_route_km: float | None = None
    distance_metric: str = "straight_line"


class FacilitySummaryOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    count: int = 0
    nearest_distance_km: float | None = None
    status: str = "available"  # available | unavailable
