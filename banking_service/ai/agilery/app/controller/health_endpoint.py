"""
Actuator-style application health endpoint.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/actuator", tags=["Health"])


@router.get("/health")
def get_health() -> dict[str, str]:
    return {"status": "UP"}
