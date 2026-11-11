"""
FastAPI application entry point for the reusable service skeleton.
"""

import logging
import os
import time
from contextlib import asynccontextmanager

from ai.agilery.app.config.settings import settings
from ai.agilery.app.controller.doc_endpoint import router as doc_router
from ai.agilery.app.controller.health_endpoint import router as health_router
from ai.agilery.app.controller.info_endpoint import router as info_router
from ai.agilery.app.controller.sbom_endpoint import router as sbom_router
from ai.agilery.app.controller import account_controller
from ai.agilery.app.controller import transaction_controller
from ai.agilery.app.db.init_db import init_db
from ai.agilery.app.exception.authentication_exception import AuthenticationException
from ai.agilery.app.exception.authorization_exception import AuthorizationException
from ai.agilery.app.exception.handlers import (
    app_validation_exception_handler,
    authentication_exception_handler,
    authorization_exception_handler,
    processing_exception_handler,
    resource_not_found_handler,
    server_error_handler,
    validation_exception_handler,
)
from ai.agilery.app.exception.processing_exception import ProcessingException
from ai.agilery.app.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)
from ai.agilery.app.exception.validation_exception import ValidationException
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

os.environ["TZ"] = "UTC"
if hasattr(time, "tzset"):
    time.tzset()  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s...", settings.SERVICE_NAME)
    init_db()
    yield
    logger.info("Shutting down %s...", settings.SERVICE_NAME)


def create_app() -> FastAPI:
    root_path = f"/{settings.SERVICE_NAME}" if settings.SERVICE_NAME else ""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.APPLICATION_VERSION,
        description=settings.SERVICE_DESCRIPTION,
        root_path=root_path,
        lifespan=lifespan,
        docs_url=None,  # Disable default docs
        redoc_url=None,  # Disable default redoc
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(ValidationException, app_validation_exception_handler)  # type: ignore
    app.add_exception_handler(ResourceNotFoundException, resource_not_found_handler)  # type: ignore
    app.add_exception_handler(AuthenticationException, authentication_exception_handler)  # type: ignore
    app.add_exception_handler(AuthorizationException, authorization_exception_handler)  # type: ignore
    app.add_exception_handler(ProcessingException, processing_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, server_error_handler)

    app.include_router(info_router)
    app.include_router(health_router)
    app.include_router(sbom_router)
    app.include_router(doc_router, prefix="/docs")

    # Register business domain routers
    app.include_router(account_controller.router)
    app.include_router(transaction_controller.router)

    app.mount("/static", StaticFiles(directory="static"), name="static")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
