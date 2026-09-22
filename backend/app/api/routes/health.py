"""Health liveness route (07_API_CONTRACT.md ?7.16, 15_DEPLOYMENT.md ?health)."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"], response_model=dict)
async def health() -> dict:
    """Liveness. Never contains secrets or internals (MASTER_PROMPT ?31)."""
    return {"status": "ok"}
