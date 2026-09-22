"""SafeRoute AI — FastAPI application factory (Phase 1 foundation).

Builds the app, wires configuration, DB, routers, middleware (request-id,
structured logging), and health checks per `07_API_CONTRACT.md` & `15_DEPLOYMENT.md`.

Run:
    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.db import init_db

logger = logging.getLogger("saferoute")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize database; graceful shutdown."""
    init_db()
    yield
    # Future: close pools, cancel running jobs, flush logs.


def create_app(settings: Any | None = None) -> FastAPI:
    """Application factory. `settings` override is for tests/injection."""
    cfg = settings or get_settings()

    app = FastAPI(
        title="SafeRoute AI API",
        version="0.1.0",
        description=(
            "SafeRoute AI — Intelligent Road Safety Navigation System.\n\n"
            "Route analysis pipeline: Routing (OSRM) → Road imagery → OpenCV\n"
            "→ YOLO11 hazard detection → aggregated hazards → deterministic\n"
            "risk score → facility intelligence → grounded LLM explanation.\n\n"
            "The LLM is an explanation layer only and never computes risk."
        ),
        openapi_url=f"{cfg.api_v1_prefix}/openapi.json",
        docs_url=f"{cfg.api_v1_prefix}/docs",
        redoc_url=f"{cfg.api_v1_prefix}/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=cfg.api_v1_prefix)

    logger.info(
        "app_started",
        extra={
            "environment": cfg.app_env,
            "routing_provider": cfg.routing_provider,
            "facility_provider": cfg.facility_provider,
            "model_configured": cfg.model_configured,
            "risk_engine_version": cfg.risk_engine_version,
        },
    )

    return app


app = create_app()
