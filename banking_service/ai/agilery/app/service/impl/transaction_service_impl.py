"""
Transaction Service Implementation.
"""

import logging
from decimal import Decimal

from fastapi import Depends
from sqlalchemy import asc, desc
from sqlmodel import col

from ai.agilery.app.dto.page import PageInfo, PageResponse
from ai.agilery.app.dto.transaction import (
    TransactionCreateDto,
    TransactionDto,
    TransactionPatchDto,
    TransactionUpdateDto,
)
from ai.agilery.app.entity.transaction import Transaction
from ai.agilery.app.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)
from ai.agilery.app.exception.validation_exception import ValidationException
from ai.agilery.app.mapper.transaction_mapper import transaction_mapper
from ai.agilery.app.repositories.account_repository import AccountRepository
from ai.agilery.app.repositories.transaction_repository import TransactionRepository
from ai.agilery.app.security.jwt import get_current_user
from ai.agilery.app.service.transaction_service import TransactionService
from ai.agilery.app.util.audit import apply_created_audit, apply_modified_audit

logger = logging.getLogger(__name__)


class TransactionServiceImpl(TransactionService):
    """
    Implementation of TransactionService.
    """

    def __init__(
        self,
        transaction_repo: TransactionRepository = Depends(),
        account_repo: AccountRepository = Depends(),
        user: dict = Depends(get_current_user),
    ):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo
        self.current_user = user

    # -----------------------------------------------
    # Helpers
    # -----------------------------------------------

    def _parse_sort(self, sort: str | None):
        """
        Parse sort parameter into SQLAlchemy order_by expression.

        Args:
            sort: Sort string in format 'field,direction'

        Returns:
            SQLAlchemy order_by expression or None
        """
        if not sort:
            return None
        try:
            field, direction = sort.split(",")
        except ValueError:
            raise ValidationException(
                description="Invalid sort format. Expected 'field,asc|desc'"
            )

        allowed_fields = {
            "createdDateTime": Transaction.created_date_time,
            "lastModifiedDateTime": Transaction.last_modified_date_time,
            "transactionId": Transaction.transaction_id,
            "amount": Transaction.amount,
            "transactionType": Transaction.transaction_type,
        }

        if field not in allowed_fields:
            raise ValidationException(description=f"Invalid sort field: {field}")
        if direction not in {"asc", "desc"}:
            raise ValidationException(
                description=f"Invalid sort direction: {direction}"
            )

        return (
            asc(col(allowed_fields[field]))
            if direction == "asc"
            else desc(col(allowed_fields[field]))
        )

    def _validate_accounts_exist(
        self, from_account_id: int, to_account_id: int
    ) -> None:
        """
        Validate that both accounts exist and are not deleted.

        Args:
            from_account_id: Source account ID
            to_account_id: Destination account ID

        Raises:
            ValidationException: If either account does not exist or is deleted
        """
        from_account = self.account_repo.get_by_id(from_account_id)
        if not from_account or from_account.is_deleted:
            raise ValidationException(
                description=f"Source account with ID '{from_account_id}' not found."
            )

        to_account = self.account_repo.get_by_id(to_account_id)
        if not to_account or to_account.is_deleted:
            raise ValidationException(
                description=f"Destination account with ID '{to_account_id}' not found."
            )

    def _validate_sufficient_balance(
        self, from_account_id: int, amount: Decimal
    ) -> None:
        """
        Validate that the source account has sufficient balance.

        Args:
            from_account_id: Source account ID
            amount: Transaction amount

        Raises:
            ValidationException: If insufficient balance
        """
        from_account = self.account_repo.get_by_id(from_account_id)
        if from_account and from_account.balance < amount:
            logger.warning(
                "Insufficient balance for account %s. Available: %s, Required: %s",
                from_account_id,
                from_account.balance,
                amount,
            )
            raise ValidationException(
                description=f"Insufficient balance in account '{from_account_id}' for the requested transaction."
            )

    def _update_account_balances(
        self, from_account_id: int, to_account_id: int, amount: Decimal
    ) -> None:
        """
        Update account balances after a transaction.

        Args:
            from_account_id: Source account ID
            to_account_id: Destination account ID
            amount: Transaction amount
        """
        from_account = self.account_repo.get_by_id(from_account_id)
        to_account = self.account_repo.get_by_id(to_account_id)

        if from_account:
            from_account.balance -= amount
            apply_modified_audit(from_account, self.current_user)
            self.account_repo.save(from_account)

        if to_account:
            to_account.balance += amount
            apply_modified_audit(to_account, self.current_user)
            self.account_repo.save(to_account)

    def _reverse_account_balances(
        self, from_account_id: int, to_account_id: int, amount: Decimal
    ) -> None:
        """
        Reverse account balances (used when updating/deleting transactions).

        Args:
            from_account_id: Source account ID
            to_account_id: Destination account ID
            amount: Transaction amount
        """
        from_account = self.account_repo.get_by_id(from_account_id)
        to_account = self.account_repo.get_by_id(to_account_id)

        if from_account:
            from_account.balance += amount
            apply_modified_audit(from_account, self.current_user)
            self.account_repo.save(from_account)

        if to_account:
            to_account.balance -= amount
            apply_modified_audit(to_account, self.current_user)
            self.account_repo.save(to_account)

    # -----------------------------------------------
    # CRUD Operations
    # -----------------------------------------------

    def create(self, dto: TransactionCreateDto) -> TransactionDto:
        """
        Create a new transaction and update account balances.

        Args:
            dto: Transaction creation data

        Returns:
            Created transaction DTO
        """
        logger.info("Creating transaction with transaction ID: %s", dto.transaction_id)

        # Check uniqueness of transaction ID
        existing_by_transaction_id = self.transaction_repo.get_by_transaction_id(
            dto.transaction_id
        )
        if existing_by_transaction_id and not existing_by_transaction_id.is_deleted:
            raise ValidationException(
                description=f"Transaction with transaction ID '{dto.transaction_id}' already exists."
            )

        # Validate accounts exist
        self._validate_accounts_exist(dto.from_account_id, dto.to_account_id)

        # Validate sufficient balance
        self._validate_sufficient_balance(dto.from_account_id, dto.amount)

        # Create transaction entity
        entity = transaction_mapper.to_entity(dto)
        apply_created_audit(entity, self.current_user)
        entity = self.transaction_repo.save(entity)

        # Update account balances
        self._update_account_balances(
            dto.from_account_id, dto.to_account_id, dto.amount
        )

        logger.info("Transaction created with ID: %s", entity.id)
        return transaction_mapper.to_dto(entity)

    def get(self, transaction_id: int) -> TransactionDto:
        """
        Retrieve a transaction by ID.

        Args:
            transaction_id: ID of the transaction

        Returns:
            Transaction DTO
        """
        existing = self.transaction_repo.get_by_id(transaction_id)
        if not existing or existing.is_deleted:
            raise ResourceNotFoundException(
                f"Transaction with ID '{transaction_id}' not found."
            )
        return transaction_mapper.to_dto(existing)

    def get_all(self, page: int, size: int, sort: str | None) -> PageResponse:
        """
        Retrieve all transactions with pagination and sorting.

        Args:
            page: Page number (0-indexed)
            size: Page size
            sort: Sort specification

        Returns:
            Paginated response containing transaction DTOs
        """
        order_by = self._parse_sort(sort)
        offset = page * size
        items = self.transaction_repo.get_paginated(
            offset=offset, limit=size, order_by=order_by
        )
        total = self.transaction_repo.count()
        total_pages = (total + size - 1) // size if size > 0 else 0

        return PageResponse(
            content=[transaction_mapper.to_dto(transaction) for transaction in items],
            page=PageInfo(
                size=size,
                number=page,
                total_elements=total,
                total_pages=total_pages,
            ),
        )

    def update(self, transaction_id: int, dto: TransactionUpdateDto) -> TransactionDto:
        """
        Update an existing transaction and adjust account balances.

        Args:
            transaction_id: ID of the transaction to update
            dto: Transaction update data

        Returns:
            Updated transaction DTO
        """
        logger.info("Updating transaction with ID: %s", transaction_id)
        existing = self.transaction_repo.get_by_id(transaction_id)
        if not existing or existing.is_deleted:
            raise ResourceNotFoundException(
                f"Transaction with ID '{transaction_id}' not found."
            )

        # Check uniqueness of transaction ID if changed
        if dto.transaction_id != existing.transaction_id:
            existing_by_transaction_id = self.transaction_repo.get_by_transaction_id(
                dto.transaction_id
            )
            if existing_by_transaction_id and not existing_by_transaction_id.is_deleted:
                raise ValidationException(
                    description=f"Transaction with transaction ID '{dto.transaction_id}' already exists."
                )

        # Validate new accounts exist
        self._validate_accounts_exist(dto.from_account_id, dto.to_account_id)

        # Reverse old transaction balances
        self._reverse_account_balances(
            existing.from_account_id, existing.to_account_id, existing.amount
        )

        # Validate sufficient balance for new transaction
        self._validate_sufficient_balance(dto.from_account_id, dto.amount)

        # Update transaction
        transaction_mapper.update(existing, dto)
        apply_modified_audit(existing, self.current_user)
        existing = self.transaction_repo.save(existing)

        # Apply new transaction balances
        self._update_account_balances(
            dto.from_account_id, dto.to_account_id, dto.amount
        )

        logger.info("Transaction with ID '%s' updated.", transaction_id)
        return transaction_mapper.to_dto(existing)

    def patch(self, transaction_id: int, dto: TransactionPatchDto) -> TransactionDto:
        """
        Partially update an existing transaction and adjust account balances if necessary.

        Args:
            transaction_id: ID of the transaction to patch
            dto: Transaction patch data

        Returns:
            Patched transaction DTO
        """
        logger.info("Patching transaction with ID: %s", transaction_id)
        existing = self.transaction_repo.get_by_id(transaction_id)
        if not existing or existing.is_deleted:
            raise ResourceNotFoundException(
                f"Transaction with ID '{transaction_id}' not found."
            )

        # Check uniqueness of transaction ID if changed
        if (
            dto.transaction_id is not None
            and dto.transaction_id != existing.transaction_id
        ):
            existing_by_transaction_id = self.transaction_repo.get_by_transaction_id(
                dto.transaction_id
            )
            if existing_by_transaction_id and not existing_by_transaction_id.is_deleted:
                raise ValidationException(
                    description=f"Transaction with transaction ID '{dto.transaction_id}' already exists."
                )

        # Determine if we need to adjust balances
        balance_adjustment_needed = (
            dto.from_account_id is not None
            or dto.to_account_id is not None
            or dto.amount is not None
        )

        if balance_adjustment_needed:
            # Use existing values if not provided in patch
            new_from_account_id = (
                dto.from_account_id
                if dto.from_account_id is not None
                else existing.from_account_id
            )
            new_to_account_id = (
                dto.to_account_id
                if dto.to_account_id is not None
                else existing.to_account_id
            )
            new_amount = dto.amount if dto.amount is not None else existing.amount

            # Validate new accounts exist
            self._validate_accounts_exist(new_from_account_id, new_to_account_id)

            # Reverse old transaction balances
            self._reverse_account_balances(
                existing.from_account_id, existing.to_account_id, existing.amount
            )

            # Validate sufficient balance for new transaction
            self._validate_sufficient_balance(new_from_account_id, new_amount)

            # Update transaction
            transaction_mapper.patch(existing, dto)
            apply_modified_audit(existing, self.current_user)
            existing = self.transaction_repo.save(existing)

            # Apply new transaction balances
            self._update_account_balances(
                new_from_account_id, new_to_account_id, new_amount
            )
        else:
            # No balance adjustment needed, just update the transaction
            transaction_mapper.patch(existing, dto)
            apply_modified_audit(existing, self.current_user)
            existing = self.transaction_repo.save(existing)

        logger.info("Transaction with ID '%s' patched.", transaction_id)
        return transaction_mapper.to_dto(existing)

    def delete(self, transaction_id: int) -> None:
        """
        Soft delete a transaction and reverse account balances.

        Args:
            transaction_id: ID of the transaction to delete
        """
        logger.info("Deleting transaction with ID: %s", transaction_id)
        existing = self.transaction_repo.get_by_id(transaction_id)
        if not existing or existing.is_deleted:
            raise ResourceNotFoundException(
                f"Transaction with ID '{transaction_id}' not found."
            )

        # Reverse transaction balances
        self._reverse_account_balances(
            existing.from_account_id, existing.to_account_id, existing.amount
        )

        # Soft delete: set is_deleted flag
        existing.is_deleted = True
        apply_modified_audit(existing, self.current_user)
        self.transaction_repo.save(existing)
        logger.info("Transaction with ID '%s' soft-deleted.", transaction_id)
