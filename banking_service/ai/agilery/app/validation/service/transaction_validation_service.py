from __future__ import annotations
import logging
from fastapi import Depends
from sqlmodel import Session

from ai.agilery.app.db.session import get_db
from ai.agilery.app.repositories.transaction_repository import TransactionRepository
from ai.agilery.app.repositories.account_repository import AccountRepository
from ai.agilery.app.dto.transaction import (
    TransactionCreateDto,
    TransactionUpdateDto,
    TransactionPatchDto,
)
from ai.agilery.app.dto.error import ValidationErrorDto
from ai.agilery.app.exception.validation_exception import ValidationException
from ai.agilery.app.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)
from ai.agilery.app.validation.chain.transaction_create_validation_chain import (
    TransactionCreateValidationChain,
)
from ai.agilery.app.validation.chain.transaction_update_validation_chain import (
    TransactionUpdateValidationChain,
)

logger = logging.getLogger(__name__)


class TransactionValidationService:
    """Validation service for Transaction entity operations.

    Orchestrates validation logic for transaction creation, updates, patches,
    retrieval, and deletion operations.
    """

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.transaction_repository = TransactionRepository(db)
        self.account_repository = AccountRepository(db)

    def on_create(self, dto: TransactionCreateDto) -> None:
        """Validate transaction creation.

        Args:
            dto: Transaction creation data transfer object

        Raises:
            ValidationException: If validation rules are violated
        """
        logger.info(
            "Validating transaction creation for transaction ID: %s", dto.transaction_id
        )

        chain = TransactionCreateValidationChain(
            self.transaction_repository, self.account_repository
        )
        errors = chain.validate(dto)

        if errors:
            logger.warning(
                "Transaction creation validation failed with %d errors", len(errors)
            )
            raise ValidationException(validation_errors=errors)

        logger.info("Transaction creation validation passed")

    def on_update(self, dto: TransactionUpdateDto) -> None:
        """Validate transaction update.

        Args:
            dto: Transaction update data transfer object

        Raises:
            ResourceNotFoundException: If transaction does not exist
            ValidationException: If validation rules are violated
        """
        logger.info("Validating transaction update for ID: %s", dto.id)

        # Check if transaction exists
        existing = self.transaction_repository.get_by_id(dto.id)
        if not existing or existing.is_deleted:
            logger.error("Transaction with ID '%s' not found", dto.id)
            raise ResourceNotFoundException(
                f"Transaction with ID '{dto.id}' not found."
            )

        chain = TransactionUpdateValidationChain(
            self.transaction_repository, self.account_repository, existing
        )
        errors = chain.validate(dto)

        if errors:
            logger.warning(
                "Transaction update validation failed with %d errors", len(errors)
            )
            raise ValidationException(validation_errors=errors)

        logger.info("Transaction update validation passed")

    def on_patch(self, dto: TransactionPatchDto) -> None:
        """Validate transaction patch.

        Args:
            dto: Transaction patch data transfer object

        Raises:
            ResourceNotFoundException: If transaction does not exist
            ValidationException: If validation rules are violated
        """
        logger.info("Validating transaction patch for ID: %s", dto.id)

        # Check if transaction exists
        existing = self.transaction_repository.get_by_id(dto.id)
        if not existing or existing.is_deleted:
            logger.error("Transaction with ID '%s' not found", dto.id)
            raise ResourceNotFoundException(
                f"Transaction with ID '{dto.id}' not found."
            )

        errors: list[ValidationErrorDto] = []

        # Validate transaction_id uniqueness if being patched
        if (
            dto.transaction_id is not None
            and dto.transaction_id != existing.transaction_id
        ):
            duplicate = self.transaction_repository.get_by_transaction_id(
                dto.transaction_id
            )
            if duplicate and duplicate.id != existing.id and not duplicate.is_deleted:
                errors.append(
                    ValidationErrorDto(
                        object_name="transactionDto",
                        field="transactionId",
                        message=f"Transaction ID '{dto.transaction_id}' is already in use.",
                    )
                )

        # Validate accounts exist if being patched
        if dto.from_account_id is not None:
            from_account = self.account_repository.get_by_id(dto.from_account_id)
            if not from_account or from_account.is_deleted:
                errors.append(
                    ValidationErrorDto(
                        object_name="transactionDto",
                        field="fromAccountId",
                        message=f"From account with ID '{dto.from_account_id}' does not exist.",
                    )
                )

        if dto.to_account_id is not None:
            to_account = self.account_repository.get_by_id(dto.to_account_id)
            if not to_account or to_account.is_deleted:
                errors.append(
                    ValidationErrorDto(
                        object_name="transactionDto",
                        field="toAccountId",
                        message=f"To account with ID '{dto.to_account_id}' does not exist.",
                    )
                )

        # Validate from and to accounts are different
        from_id = (
            dto.from_account_id
            if dto.from_account_id is not None
            else existing.from_account_id
        )
        to_id = (
            dto.to_account_id
            if dto.to_account_id is not None
            else existing.to_account_id
        )

        if from_id == to_id:
            errors.append(
                ValidationErrorDto(
                    object_name="transactionDto",
                    field="toAccountId",
                    message="From account and to account cannot be the same.",
                )
            )

        # Validate amount is positive if being patched
        if dto.amount is not None and dto.amount <= 0:
            errors.append(
                ValidationErrorDto(
                    object_name="transactionDto",
                    field="amount",
                    message="Transaction amount must be greater than zero.",
                )
            )

        if errors:
            logger.warning(
                "Transaction patch validation failed with %d errors", len(errors)
            )
            raise ValidationException(validation_errors=errors)

        logger.info("Transaction patch validation passed")

    def on_get(self, entity_id: int) -> None:
        """Validate transaction retrieval.

        Args:
            entity_id: Transaction ID to retrieve

        Raises:
            ResourceNotFoundException: If transaction does not exist
        """
        logger.info("Validating transaction retrieval for ID: %s", entity_id)

        existing = self.transaction_repository.get_by_id(entity_id)
        if not existing or existing.is_deleted:
            logger.error("Transaction with ID '%s' not found", entity_id)
            raise ResourceNotFoundException(
                f"Transaction with ID '{entity_id}' not found."
            )

        logger.info("Transaction retrieval validation passed")

    def on_get_all(self, page: int, size: int, sort: str | None) -> None:
        """Validate transaction list retrieval.

        Args:
            page: Page number
            size: Page size
            sort: Sort specification
        """
        logger.info("Validating transaction list retrieval")
        # No specific validation needed for get_all
        pass

    def on_delete(self, entity_id: int) -> None:
        """Validate transaction deletion.

        Args:
            entity_id: Transaction ID to delete

        Raises:
            ResourceNotFoundException: If transaction does not exist
        """
        logger.info("Validating transaction deletion for ID: %s", entity_id)

        existing = self.transaction_repository.get_by_id(entity_id)
        if not existing or existing.is_deleted:
            logger.error("Transaction with ID '%s' not found", entity_id)
            raise ResourceNotFoundException(
                f"Transaction with ID '{entity_id}' not found."
            )

        logger.info("Transaction deletion validation passed")
