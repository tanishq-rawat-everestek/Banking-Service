# --------------------------------------------------------------------
# Router setup
# --------------------------------------------------------------------
import logging

from fastapi import APIRouter, Request
from fastapi.openapi.docs import (
    get_swagger_ui_html,
)

router = APIRouter(tags=["docs"])

# --------------------------------------------------------------------
# Logger setup
# --------------------------------------------------------------------
logger = logging.getLogger(__name__)


@router.get("/", include_in_schema=False)
async def custom_swagger_ui_html(req: Request):
    # Standard production fix for OpenAPI UI behind a proxy:
    # We grab the prefix passed by the proxy, and use it to build the URLs for the static assets and OpenAPI spec.
    prefix = req.headers.get("x-forwarded-prefix", req.scope.get("root_path", ""))
    prefix = prefix.rstrip("/")

    return get_swagger_ui_html(
        swagger_js_url=f"{prefix}/static/swagger-ui-bundle.js",
        swagger_css_url=f"{prefix}/static/swagger-ui.css",
        openapi_url=f"{prefix}/openapi.json",
        title="Example Service API Docs",
    )
