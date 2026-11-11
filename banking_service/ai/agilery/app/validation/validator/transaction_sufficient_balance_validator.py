import logging

from ai.agilery.app.validation.base.validation_handler import ValidationHandler
from ai.agilery.app.dto.error import ValidationErrorDto
from ai.agilery.app.dto.transaction import TransactionCreateDto
from ai.agilery.app.repositories.account_repository import AccountRepository

logger = logging.getLogger(__name__)


class TransactionSufficientBalanceValidator(ValidationHandler[TransactionCreateDto]):
    """Validates that the from account has sufficient balance for the transaction."""

    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def validate(self, dto: TransactionCreateDto) -> list[ValidationErrorDto]:
        errors: list[ValidationErrorDto] = []

        from_account = self.account_repository.get_by_id(dto.from_account_id)

        # Only validate if account exists (existence is validated by another validator)
        if from_account and not from_account.is_deleted:
            if from_account.balance < dto.amount:
                # Log sensitive details but don't expose in error message
                logger.warning(
                    "Insufficient balance for account %s. Available: %s, Required: %s",
                    dto.from_account_id,
                    from_account.balance,
                    dto.amount,
                )
                errors.append(
                    ValidationErrorDto(
                        object_name="transactionDto",
                        field="amount",
                        message="Insufficient balance in from account for the requested transaction.",
                    )
                )

        return errors
