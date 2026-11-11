"""
Base chain-of-responsibility implementation for validation handlers.
"""

from abc import ABC
from typing import Generic, TypeVar

from ai.agilery.app.dto.error import ValidationErrorDto
from ai.agilery.app.validation.base.validation_handler import ValidationHandler

T = TypeVar("T")


class AbstractValidationChain(ABC, Generic[T]):
    def __init__(self) -> None:
        self._chain: list[ValidationHandler[T]] = []

    def add(self, handler: ValidationHandler[T]) -> None:
        self._chain.append(handler)

    def validate(self, dto: T) -> list[ValidationErrorDto]:
        errors: list[ValidationErrorDto] = []
        for handler in self._chain:
            errors.extend(handler.validate(dto))
        return errors

    def get_chain(self) -> list[ValidationHandler[T]]:
        return self._chain
