"""
Business validation exception.
"""

from ai.agilery.app.dto.error import ValidationErrorDto


class ValidationException(Exception):
    def __init__(
        self,
        validation_errors: list[ValidationErrorDto] | None = None,
        description: str = "Bad Request",
    ):
        self.message = "Bad Request"
        self.description = description
        self.validation_errors = validation_errors or []
        super().__init__(self.message)

    @classmethod
    def from_field_error(
        cls,
        field: str,
        message: str,
        description: str = "Bad Request",
    ) -> "ValidationException":
        return cls(
            validation_errors=[ValidationErrorDto(field=field, message=message)],
            description=description,
        )
