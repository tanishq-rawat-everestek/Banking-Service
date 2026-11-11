"""
Standard API error response schemas.
"""

from pydantic import ConfigDict, Field
from fastapi_camelcase import CamelModel

MODEL_CONFIG = ConfigDict(populate_by_name=True)


class ValidationErrorDto(CamelModel):
    object_name: str | None = None
    field: str
    message: str

    model_config = MODEL_CONFIG


class ErrorResponseDto(CamelModel):
    message: str
    description: str
    validation_errors: list[ValidationErrorDto] = Field(default_factory=list)

    model_config = MODEL_CONFIG
