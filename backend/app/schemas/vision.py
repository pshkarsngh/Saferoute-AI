from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
class HazardDetectionOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    detection_id: str
    image_id: str
    route_id: str
    segment_id: str
    hazard_type: str
    confidence: float = Field(ge=0, le=1)
    bounding_box: dict | None = None
