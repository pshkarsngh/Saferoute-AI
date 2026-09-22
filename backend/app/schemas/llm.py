from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
class LLMRequestIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route_analysis_id: str


class ExplanationOut(BaseModel):
    """Grounded LLM explanation (10_LLM_SPEC.md, 07_API_CONTRACT.md ?7.16)."""

    model_config = ConfigDict(extra="forbid")
    explanation_id: str
    route_id: str
    text: str
    model: str | None = None
    prompt_version: str | None = None
    is_fallback: bool = False
