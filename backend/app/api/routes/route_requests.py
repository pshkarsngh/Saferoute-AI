"""Route-request endpoints (07_API_CONTRACT.md ?7.1).

Graceful behavior: routing provider unavailable -> 503 ROUTING_PROVIDER_ERROR.
Never fabricates routes, never fabricates distance, never returns empty as zero.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/route-requests", tags=["routes"], status_code=503)
async def create_route_request() -> JSONResponse:
    """Routing pipeline not wired to a live provider in Phase 1 scaffold.

    Returns explicit unavailable rather than a fabricated 0-route result.
    """
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "ROUTING_PROVIDER_ERROR",
                "message": "Routing provider is not configured. Route generation is unavailable.",
                "details": None,
            }
        },
    )
