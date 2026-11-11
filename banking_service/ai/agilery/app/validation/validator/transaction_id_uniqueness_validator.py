from typing import Optional

from ai.agilery.app.validation.base.validation_handler import ValidationHandler
from ai.agilery.app.dto.error import ValidationErrorDto
from ai.agilery.app.dto.transaction import TransactionCreateDto, TransactionUpdateDto
from ai.agilery.app.entity.transaction import Transaction
from ai.agilery.app.repositories.transaction_repository import TransactionRepository


class TransactionIdUniquenessValidator(
    ValidationHandler[TransactionCreateDto | TransactionUpdateDto]
):
    """Validates that transaction ID is unique across all transactions."""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        existing_transaction: Optional[Transaction] = None,
    ):
        self.transaction_repository = transaction_repository
        self.existing_transaction = existing_transaction

    def validate(
        self, dto: TransactionCreateDto | TransactionUpdateDto
    ) -> list[ValidationErrorDto]:
        errors: list[ValidationErrorDto] = []

        duplicate = self.transaction_repository.get_by_transaction_id(
            dto.transaction_id
        )

        if duplicate and not duplicate.is_deleted:
            # For updates, allow the same transaction ID if it belongs to the same transaction
            if (
                self.existing_transaction is None
                or duplicate.id != self.existing_transaction.id
            ):
                errors.append(
                    ValidationErrorDto(
                        object_name="transactionDto",
                        field="transactionId",
                        message=f"Transaction ID '{dto.transaction_id}' is already in use.",
                    )
                )

        return errors
