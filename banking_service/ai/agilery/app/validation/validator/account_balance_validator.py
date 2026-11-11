from ai.agilery.app.validation.base.validation_handler import ValidationHandler
from ai.agilery.app.dto.error import ValidationErrorDto
from ai.agilery.app.dto.account import AccountCreateDto, AccountUpdateDto


class AccountBalanceValidator(ValidationHandler[AccountCreateDto | AccountUpdateDto]):
    """Validates that account balance is non-negative."""

    def validate(
        self, dto: AccountCreateDto | AccountUpdateDto
    ) -> list[ValidationErrorDto]:
        errors: list[ValidationErrorDto] = []

        if dto.balance < 0:
            errors.append(
                ValidationErrorDto(
                    object_name="accountDto",
                    field="balance",
                    message="Balance cannot be negative.",
                )
            )

        return errors
