from ai.agilery.app.validation.base.validation_handler import ValidationHandler
from ai.agilery.app.dto.error import ValidationErrorDto
from ai.agilery.app.dto.transaction import TransactionCreateDto, TransactionUpdateDto


class TransactionAmountValidator(
    ValidationHandler[TransactionCreateDto | TransactionUpdateDto]
):
    """Validates that transaction amount is positive and does not exceed maximum limit."""

    MAX_TRANSACTION_AMOUNT = 50000

    def validate(
        self, dto: TransactionCreateDto | TransactionUpdateDto
    ) -> list[ValidationErrorDto]:
        errors: list[ValidationErrorDto] = []

        if dto.amount <= 0:
            errors.append(
                ValidationErrorDto(
                    object_name="transactionDto",
                    field="amount",
                    message="Transaction amount must be greater than zero.",
                )
            )

        if dto.amount > self.MAX_TRANSACTION_AMOUNT:
            errors.append(
                ValidationErrorDto(
                    object_name="transactionDto",
                    field="amount",
                    message=f"Transaction amount must not exceed {self.MAX_TRANSACTION_AMOUNT:,.2f}.",
                )
            )

        return errors
