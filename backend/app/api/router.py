"""API router (SafeRoute AI). Thin; routes -> health + route_requests only.

Routers are included WITHOUT a prefix: `app/main.py` mounts `api_router`
under `cfg.api_v1_prefix` (`/api/v1`), so paths resolve to `/api/v1/health`
and `/api/v1/route-requests` per `07_API_CONTRACT.md` §4/§7.
"""
from fastapi import APIRouter
from app.api.routes import health, route_requests

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(route_requests.router)
