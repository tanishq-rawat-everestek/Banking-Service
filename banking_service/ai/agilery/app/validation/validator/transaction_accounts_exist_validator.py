from ai.agilery.app.validation.base.validation_handler import ValidationHandler
from ai.agilery.app.dto.error import ValidationErrorDto
from ai.agilery.app.dto.transaction import TransactionCreateDto, TransactionUpdateDto
from ai.agilery.app.repositories.account_repository import AccountRepository


class TransactionAccountsExistValidator(
    ValidationHandler[TransactionCreateDto | TransactionUpdateDto]
):
    """Validates that both from and to accounts exist and are not deleted."""

    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def validate(
        self, dto: TransactionCreateDto | TransactionUpdateDto
    ) -> list[ValidationErrorDto]:
        errors: list[ValidationErrorDto] = []

        # Validate from account exists
        from_account = self.account_repository.get_by_id(dto.from_account_id)
        if not from_account or from_account.is_deleted:
            errors.append(
                ValidationErrorDto(
                    object_name="transactionDto",
                    field="fromAccountId",
                    message=f"From account with ID '{dto.from_account_id}' does not exist.",
                )
            )

        # Validate to account exists
        to_account = self.account_repository.get_by_id(dto.to_account_id)
        if not to_account or to_account.is_deleted:
            errors.append(
                ValidationErrorDto(
                    object_name="transactionDto",
                    field="toAccountId",
                    message=f"To account with ID '{dto.to_account_id}' does not exist.",
                )
            )

        return errors
