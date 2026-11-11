from ai.agilery.app.validation.base.validation_handler import ValidationHandler
from ai.agilery.app.dto.error import ValidationErrorDto
from ai.agilery.app.dto.transaction import TransactionCreateDto, TransactionUpdateDto


class TransactionAccountsDifferentValidator(
    ValidationHandler[TransactionCreateDto | TransactionUpdateDto]
):
    """Validates that from and to accounts are different."""

    def validate(
        self, dto: TransactionCreateDto | TransactionUpdateDto
    ) -> list[ValidationErrorDto]:
        errors: list[ValidationErrorDto] = []

        if dto.from_account_id == dto.to_account_id:
            errors.append(
                ValidationErrorDto(
                    object_name="transactionDto",
                    field="toAccountId",
                    message="From account and to account cannot be the same.",
                )
            )

        return errors
