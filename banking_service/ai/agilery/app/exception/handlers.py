"""
Global exception handlers using the common error response format.
"""

import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ai.agilery.app.exception.authentication_exception import AuthenticationException
from ai.agilery.app.exception.authorization_exception import AuthorizationException
from ai.agilery.app.exception.processing_exception import ProcessingException
from ai.agilery.app.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)
from ai.agilery.app.exception.validation_exception import ValidationException
from ai.agilery.app.dto.error import ErrorResponseDto, ValidationErrorDto

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        ValidationErrorDto(
            object_name="body",
            field=".".join(map(str, error["loc"])),
            message=error["msg"],
        )
        for error in exc.errors()
    ]
    content = ErrorResponseDto(
        message="Request is not valid",
        description=(
            "The request contains invalid or missing fields. "
            "Please check the validation errors for more details."
        ),
        validation_errors=errors,
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=content.model_dump(by_alias=True),
    )


async def app_validation_exception_handler(request: Request, exc: ValidationException):
    content = ErrorResponseDto(
        message=exc.message,
        description=exc.description,
        validation_errors=exc.validation_errors,
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=content.model_dump(by_alias=True),
    )


async def resource_not_found_handler(request: Request, exc: ResourceNotFoundException):
    content = ErrorResponseDto(
        message=exc.message,
        description=exc.description,
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=content.model_dump(by_alias=True),
    )


async def authentication_exception_handler(
    request: Request, exc: AuthenticationException
):
    content = ErrorResponseDto(
        message=exc.message,
        description=exc.description,
    )
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=content.model_dump(by_alias=True),
    )


async def authorization_exception_handler(
    request: Request, exc: AuthorizationException
):
    content = ErrorResponseDto(
        message=exc.message,
        description=exc.description,
    )
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=content.model_dump(by_alias=True),
    )


async def processing_exception_handler(request: Request, exc: ProcessingException):
    content = ErrorResponseDto(
        message=exc.message,
        description=(
            "An unexpected error has occurred on server. Please try again in 5 to 10 minutes. "
            "If the problem persists contact our support team at support@agilery.ai."
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content.model_dump(by_alias=True),
    )


async def server_error_handler(request: Request, exc: Exception):
    logger.error("Unexpected error:", exc_info=True)
    content = ErrorResponseDto(
        message="Unexpected error",
        description=(
            "An unexpected error has occurred on server. Please try after 5 to 10 minutes. "
            "If the problem persists contact our support team at support@agilery.ai."
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content.model_dump(by_alias=True),
    )
