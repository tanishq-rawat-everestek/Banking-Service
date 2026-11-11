"""
Actuator-style application info endpoint.
"""

from fastapi import APIRouter

from ai.agilery.app.config.settings import settings

router = APIRouter(prefix="/actuator", tags=["Info"])


@router.get("/info")
def get_info() -> dict[str, str]:
    return {
        "version": settings.APPLICATION_VERSION,
        "description": settings.SERVICE_DESCRIPTION,
        "serviceName": settings.SERVICE_NAME,
        "appVersion": settings.APP_VERSION,
    }
