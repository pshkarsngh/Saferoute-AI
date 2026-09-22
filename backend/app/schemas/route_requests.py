from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
class Location(BaseModel):
    """Geocoded/coordinates location. Coordinates are always validated ranges."""

    model_config = ConfigDict(extra="forbid")
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    name: str | None = None


class RouteRequestIn(BaseModel):
    """POST /api/v1/route-requests body (07_API_CONTRACT.md ?7.1)."""

    model_config = ConfigDict(extra="forbid")
    source: Location
    destination: Location
