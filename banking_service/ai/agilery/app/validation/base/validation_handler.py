"""
Base interface for validation handlers.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ai.agilery.app.dto.error import ValidationErrorDto

T = TypeVar("T")


class ValidationHandler(ABC, Generic[T]):
    @abstractmethod
    def validate(self, dto: T) -> list[ValidationErrorDto]:
        pass
