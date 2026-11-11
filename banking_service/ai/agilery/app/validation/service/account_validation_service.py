from __future__ import annotations
import logging
from fastapi import Depends
from sqlmodel import Session

from ai.agilery.app.db.session import get_db
from ai.agilery.app.repositories.account_repository import AccountRepository
from ai.agilery.app.dto.account import (
    AccountCreateDto,
    AccountUpdateDto,
    AccountPatchDto,
)
from ai.agilery.app.dto.error import ValidationErrorDto
from ai.agilery.app.exception.validation_exception import ValidationException
from ai.agilery.app.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)
from ai.agilery.app.validation.chain.account_create_validation_chain import (
    AccountCreateValidationChain,
)
from ai.agilery.app.validation.chain.account_update_validation_chain import (
    AccountUpdateValidationChain,
)

logger = logging.getLogger(__name__)


class AccountValidationService:
    """Validation service for Account entity operations.

    Orchestrates validation logic for account creation, updates, patches,
    retrieval, and deletion operations.
    """

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.account_repository = AccountRepository(db)

    def on_create(self, dto: AccountCreateDto) -> None:
        """Validate account creation.

        Args:
            dto: Account creation data transfer object

        Raises:
            ValidationException: If validation rules are violated
        """
        logger.info(
            "Validating account creation for account number: %s", dto.account_number
        )

        chain = AccountCreateValidationChain(self.account_repository)
        errors = chain.validate(dto)

        if errors:
            logger.warning(
                "Account creation validation failed with %d errors", len(errors)
            )
            raise ValidationException(validation_errors=errors)

        logger.info("Account creation validation passed")

    def on_update(self, dto: AccountUpdateDto) -> None:
        """Validate account update.

        Args:
            dto: Account update data transfer object

        Raises:
            ResourceNotFoundException: If account does not exist
            ValidationException: If validation rules are violated
        """
        logger.info("Validating account update for ID: %s", dto.id)

        # Check if account exists
        existing = self.account_repository.get_by_id(dto.id)
        if not existing or existing.is_deleted:
            logger.error("Account with ID '%s' not found", dto.id)
            raise ResourceNotFoundException(f"Account with ID '{dto.id}' not found.")

        chain = AccountUpdateValidationChain(self.account_repository, existing)
        errors = chain.validate(dto)

        if errors:
            logger.warning(
                "Account update validation failed with %d errors", len(errors)
            )
            raise ValidationException(validation_errors=errors)

        logger.info("Account update validation passed")

    def on_patch(self, dto: AccountPatchDto) -> None:
        """Validate account patch.

        Args:
            dto: Account patch data transfer object

        Raises:
            ResourceNotFoundException: If account does not exist
            ValidationException: If validation rules are violated
        """
        logger.info("Validating account patch for ID: %s", dto.id)

        # Check if account exists
        existing = self.account_repository.get_by_id(dto.id)
        if not existing or existing.is_deleted:
            logger.error("Account with ID '%s' not found", dto.id)
            raise ResourceNotFoundException(f"Account with ID '{dto.id}' not found.")

        errors: list[ValidationErrorDto] = []

        # Validate uniqueness constraints only for fields being patched
        if (
            dto.account_number is not None
            and dto.account_number != existing.account_number
        ):
            duplicate = self.account_repository.get_by_account_number(
                dto.account_number
            )
            if duplicate and duplicate.id != existing.id and not duplicate.is_deleted:
                errors.append(
                    ValidationErrorDto(
                        object_name="accountDto",
                        field="accountNumber",
                        message=f"Account number '{dto.account_number}' is already in use.",
                    )
                )

        if dto.email is not None and dto.email != existing.email:
            duplicate = self.account_repository.get_by_email(dto.email)
            if duplicate and duplicate.id != existing.id and not duplicate.is_deleted:
                errors.append(
                    ValidationErrorDto(
                        object_name="accountDto",
                        field="email",
                        message=f"Email '{dto.email}' is already in use.",
                    )
                )

        if dto.phone_number is not None and dto.phone_number != existing.phone_number:
            duplicate = self.account_repository.get_by_phone_number(dto.phone_number)
            if duplicate and duplicate.id != existing.id and not duplicate.is_deleted:
                errors.append(
                    ValidationErrorDto(
                        object_name="accountDto",
                        field="phoneNumber",
                        message=f"Phone number '{dto.phone_number}' is already in use.",
                    )
                )

        if dto.balance is not None and dto.balance < 0:
            errors.append(
                ValidationErrorDto(
                    object_name="accountDto",
                    field="balance",
                    message="Balance cannot be negative.",
                )
            )

        if errors:
            logger.warning(
                "Account patch validation failed with %d errors", len(errors)
            )
            raise ValidationException(validation_errors=errors)

        logger.info("Account patch validation passed")

    def on_get(self, entity_id: int) -> None:
        """Validate account retrieval.

        Args:
            entity_id: Account ID to retrieve

        Raises:
            ResourceNotFoundException: If account does not exist
        """
        logger.info("Validating account retrieval for ID: %s", entity_id)

        existing = self.account_repository.get_by_id(entity_id)
        if not existing or existing.is_deleted:
            logger.error("Account with ID '%s' not found", entity_id)
            raise ResourceNotFoundException(f"Account with ID '{entity_id}' not found.")

        logger.info("Account retrieval validation passed")

    def on_get_all(self, page: int, size: int, sort: str | None) -> None:
        """Validate account list retrieval.

        Args:
            page: Page number
            size: Page size
            sort: Sort specification
        """
        logger.info("Validating account list retrieval")
        # No specific validation needed for get_all
        pass

    def on_delete(self, entity_id: int) -> None:
        """Validate account deletion.

        Args:
            entity_id: Account ID to delete

        Raises:
            ResourceNotFoundException: If account does not exist
        """
        logger.info("Validating account deletion for ID: %s", entity_id)

        existing = self.account_repository.get_by_id(entity_id)
        if not existing or existing.is_deleted:
            logger.error("Account with ID '%s' not found", entity_id)
            raise ResourceNotFoundException(f"Account with ID '{entity_id}' not found.")

        logger.info("Account deletion validation passed")
