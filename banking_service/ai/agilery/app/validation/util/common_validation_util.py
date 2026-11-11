"""
Common helpers for converting validation results into exceptions.
"""

from ai.agilery.app.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)
from ai.agilery.app.exception.validation_exception import ValidationException
from ai.agilery.app.dto.error import ValidationErrorDto


class CommonValidationUtil:
    def throw_validation_exception(self, errors: list[ValidationErrorDto]) -> None:
        if errors:
            raise ValidationException(errors)

    def throw_resource_not_found_exception(
        self,
        errors: list[ValidationErrorDto],
        message: str,
    ) -> None:
        if errors:
            raise ResourceNotFoundException(message)
