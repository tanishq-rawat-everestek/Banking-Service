"""
Transaction Service interface — defines the contract for transaction business logic.
"""

from abc import ABC, abstractmethod

from ai.agilery.app.dto.page import PageResponse
from ai.agilery.app.dto.transaction import (
    TransactionCreateDto,
    TransactionDto,
    TransactionPatchDto,
    TransactionUpdateDto,
)


class TransactionService(ABC):
    """
    Abstract service interface for Transaction operations.
    """

    @abstractmethod
    def create(self, dto: TransactionCreateDto) -> TransactionDto:
        """
        Create a new transaction.

        Args:
            dto: Transaction creation data

        Returns:
            Created transaction DTO
        """
        ...

    @abstractmethod
    def update(self, transaction_id: int, dto: TransactionUpdateDto) -> TransactionDto:
        """
        Update an existing transaction.

        Args:
            transaction_id: ID of the transaction to update
            dto: Transaction update data

        Returns:
            Updated transaction DTO
        """
        ...

    @abstractmethod
    def patch(self, transaction_id: int, dto: TransactionPatchDto) -> TransactionDto:
        """
        Partially update an existing transaction.

        Args:
            transaction_id: ID of the transaction to patch
            dto: Transaction patch data

        Returns:
            Patched transaction DTO
        """
        ...

    @abstractmethod
    def get(self, transaction_id: int) -> TransactionDto:
        """
        Retrieve a transaction by ID.

        Args:
            transaction_id: ID of the transaction

        Returns:
            Transaction DTO
        """
        ...

    @abstractmethod
    def get_all(self, page: int, size: int, sort: str | None) -> PageResponse:
        """
        Retrieve all transactions with pagination and sorting.

        Args:
            page: Page number (0-indexed)
            size: Page size
            sort: Sort specification (e.g., 'createdDateTime,asc')

        Returns:
            Paginated response containing transaction DTOs
        """
        ...

    @abstractmethod
    def delete(self, transaction_id: int) -> None:
        """
        Soft delete a transaction.

        Args:
            transaction_id: ID of the transaction to delete
        """
        ...
