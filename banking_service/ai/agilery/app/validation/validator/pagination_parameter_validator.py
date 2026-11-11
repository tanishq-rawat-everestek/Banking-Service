"""
Generic validator for pagination and sorting parameters.
"""

from typing import Any

from ai.agilery.app.dto.error import ValidationErrorDto
from ai.agilery.app.validation.base.validation_handler import ValidationHandler


class PaginationParameterValidator(ValidationHandler[dict[str, Any]]):
    def __init__(self, allowed_sort_fields: set[str], object_name: str):
        self.allowed_sort_fields = allowed_sort_fields
        self.object_name = object_name

    def validate(self, dto: dict[str, Any]) -> list[ValidationErrorDto]:
        errors: list[ValidationErrorDto] = []
        sort = dto.get("sort")

        if sort is None:
            return errors

        try:
            sort_field = sort.split(",")[0]
        except Exception:
            errors.append(
                ValidationErrorDto(
                    object_name=self.object_name,
                    field="sort",
                    message="Invalid sort format. Expected 'field,asc|desc'.",
                )
            )
            return errors

        if sort_field not in self.allowed_sort_fields:
            errors.append(
                ValidationErrorDto(
                    object_name=self.object_name,
                    field="sort",
                    message=(
                        f"Sorting by '{sort_field}' is not allowed. "
                        f"Allowed fields are: {sorted(self.allowed_sort_fields)}"
                    ),
                )
            )

        return errors
