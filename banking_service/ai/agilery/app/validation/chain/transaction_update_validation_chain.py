from ai.agilery.app.validation.base.abstract_validation_chain import (
    AbstractValidationChain,
)
from ai.agilery.app.dto.transaction import TransactionUpdateDto
from ai.agilery.app.entity.transaction import Transaction
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


class TransactionUpdateValidationChain(AbstractValidationChain[TransactionUpdateDto]):
    """Validation chain for transaction update.

    Validates business rules for updating an existing transaction including
    uniqueness, account existence, amount validity, and account differences.
    """

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
        existing_transaction: Transaction,
    ) -> None:
        super().__init__()
        self.add(
            TransactionIdUniquenessValidator(
                transaction_repository, existing_transaction
            )
        )
        self.add(TransactionAccountsExistValidator(account_repository))
        self.add(TransactionAccountsDifferentValidator())
        self.add(TransactionAmountValidator())
