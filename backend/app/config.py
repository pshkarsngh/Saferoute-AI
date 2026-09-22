"""Applications settings for SafeRoute AI.

All values are read from environment variables (via pydantic-settings) with
development-safe defaults. Never hard-code secrets; never commit a real .env.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App -------------------------------------------------------------
    app_name: str = "SafeRoute AI"
    app_env: str = "development"  # development | testing | production
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    log_level: str = "INFO"

    # --- Database --------------------------------------------------------
    # Default to SQLite so the app runs with zero setup for dev/tests.
    # Production/compose must override with PostgreSQL.
    database_url: str = "sqlite:///./saferoute.db"

    # --- Routing provider -------------------------------------------------
    routing_provider: str = "osrm"  # osrm | mock (mock is DEMO-only)
    routing_base_url: str = "https://router.project-osrm.org"
    max_candidate_routes: int = 4

    # --- Route segmentation ----------------------------------------------
    segment_length_meters: int = 500

    # --- Facility provider ------------------------------------------------
    facility_provider: str = "overpass"  # overpass | mock (mock is DEMO-only)
    overpass_base_url: str = "https://overpass-api.de/api/interpreter"
    facility_search_radius_km: float = 1.0
    max_facility_results: int = 200

    # --- Vision / ML ------------------------------------------------------
    model_path: str = ""  # e.g. ml/models/best.pt; empty => YOLO unavailable
    model_name: str = "SafeRoute-YOLO11"
    model_version: str = "0.0.0"
    yolo_confidence_threshold: float = 0.50
    yolo_iou_threshold: float = 0.45
    image_max_size_mb: int = 10
    image_max_width: int = 4096
    image_max_height: int = 4096

    # --- Hazard aggregation ----------------------------------------------
    cluster_radius_m: float = 30.0

    # --- Risk engine ------------------------------------------------------
    # Format: class:weight pairs. Severities are fixed per class in the engine.
    hazard_weights: str = "pothole:3,road_crack:2,damaged_road:2,obstacle:1,debris:1"
    risk_scale_max: float = 100.0
    risk_norm_gain: float = 1.25
    risk_engine_version: str = "1.0"

    # --- LLM (explanation layer only) ------------------------------------
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_timeout_s: float = 25.0
    llm_prompt_version: str = "v1"

    # --- HTTP / rate limiting ---------------------------------------------
    request_timeout_s: float = 15.0
    rate_limit_per_minute: int = 60
    cors_origins: str = "http://localhost:5173"

    # --- Derived helpers ---------------------------------------------------
    @property
    def hazard_weight_map(self) -> dict[str, float]:
        weights: dict[str, float] = {}
        for pair in self.hazard_weights.split(","):
            if not pair.strip():
                continue
            name, _, value = pair.partition(":")
            weights[name.strip()] = float(value)
        return weights

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def model_configured(self) -> bool:
        return bool(self.model_path) and Path(self.model_path).exists()


@lru_cache
def get_settings() -> Settings:
    return Settings()