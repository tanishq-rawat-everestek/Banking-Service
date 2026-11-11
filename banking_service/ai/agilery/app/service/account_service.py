"""
Account Service interface — defines the contract for account business logic.
"""

from abc import ABC, abstractmethod

from ai.agilery.app.dto.account import (
    AccountCreateDto,
    AccountDto,
    AccountPatchDto,
    AccountUpdateDto,
)
from ai.agilery.app.dto.page import PageResponse


class AccountService(ABC):
    """
    Abstract service interface for Account operations.
    """

    @abstractmethod
    def create(self, dto: AccountCreateDto) -> AccountDto:
        """
        Create a new account.

        Args:
            dto: Account creation data

        Returns:
            Created account DTO
        """
        ...

    @abstractmethod
    def update(self, account_id: int, dto: AccountUpdateDto) -> AccountDto:
        """
        Update an existing account.

        Args:
            account_id: ID of the account to update
            dto: Account update data

        Returns:
            Updated account DTO
        """
        ...

    @abstractmethod
    def patch(self, account_id: int, dto: AccountPatchDto) -> AccountDto:
        """
        Partially update an existing account.

        Args:
            account_id: ID of the account to patch
            dto: Account patch data

        Returns:
            Patched account DTO
        """
        ...

    @abstractmethod
    def get(self, account_id: int) -> AccountDto:
        """
        Retrieve an account by ID.

        Args:
            account_id: ID of the account

        Returns:
            Account DTO
        """
        ...

    @abstractmethod
    def get_all(self, page: int, size: int, sort: str | None) -> PageResponse:
        """
        Retrieve all accounts with pagination and sorting.

        Args:
            page: Page number (0-indexed)
            size: Page size
            sort: Sort specification (e.g., 'createdDateTime,asc')

        Returns:
            Paginated response containing account DTOs
        """
        ...

    @abstractmethod
    def delete(self, account_id: int) -> None:
        """
        Soft delete an account.

        Args:
            account_id: ID of the account to delete
        """
        ...
