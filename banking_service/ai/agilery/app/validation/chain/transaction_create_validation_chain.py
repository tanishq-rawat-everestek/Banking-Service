from ai.agilery.app.validation.base.abstract_validation_chain import (
    AbstractValidationChain,
)
from ai.agilery.app.dto.transaction import TransactionCreateDto
from ai.agilery.app.repositories.transaction_repository import TransactionRepository
from ai.agilery.app.repositories.account_repository import AccountRepository
from ai.agilery.app.validation.validator.transaction_id_uniqueness_validator import (
    TransactionIdUniquenessValidator,
)
from ai.agilery.app.validation.validator.transaction_accounts_exist_validator import (
    TransactionAccountsExistValidator,
)
from ai.agilery.app.validation.validator.transaction_accounts_different_validator import (
    TransactionAccountsDifferentValidator,
)
from ai.agilery.app.validation.validator.transaction_amount_validator import (
    TransactionAmountValidator,
)
from ai.agilery.app.validation.validator.transaction_sufficient_balance_validator import (
    TransactionSufficientBalanceValidator,
)


class TransactionCreateValidationChain(AbstractValidationChain[TransactionCreateDto]):
    """Validation chain for transaction creation.

    Validates business rules for creating a new transaction including
    uniqueness, account existence, amount validity, and sufficient balance.
    """

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
    ) -> None:
        super().__init__()
        self.add(TransactionIdUniquenessValidator(transaction_repository))
        self.add(TransactionAccountsExistValidator(account_repository))
        self.add(TransactionAccountsDifferentValidator())
        self.add(TransactionAmountValidator())
        self.add(TransactionSufficientBalanceValidator(account_repository))
