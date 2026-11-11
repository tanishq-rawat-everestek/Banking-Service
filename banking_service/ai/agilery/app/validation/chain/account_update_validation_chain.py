from ai.agilery.app.validation.base.abstract_validation_chain import (
    AbstractValidationChain,
)
from ai.agilery.app.dto.account import AccountUpdateDto
from ai.agilery.app.entity.account import Account
from ai.agilery.app.repositories.account_repository import AccountRepository
from ai.agilery.app.validation.validator.account_number_uniqueness_validator import (
    AccountNumberUniquenessValidator,
)
from ai.agilery.app.validation.validator.account_email_uniqueness_validator import (
    AccountEmailUniquenessValidator,
)
from ai.agilery.app.validation.validator.account_phone_uniqueness_validator import (
    AccountPhoneUniquenessValidator,
)
from ai.agilery.app.validation.validator.account_balance_validator import (
    AccountBalanceValidator,
)


class AccountUpdateValidationChain(AbstractValidationChain[AccountUpdateDto]):
    """Validation chain for account update.

    Validates business rules for updating an existing account including
    uniqueness constraints and balance requirements.
    """

    def __init__(
        self, account_repository: AccountRepository, existing_account: Account
    ) -> None:
        super().__init__()
        self.add(AccountNumberUniquenessValidator(account_repository, existing_account))
        self.add(AccountEmailUniquenessValidator(account_repository, existing_account))
        self.add(AccountPhoneUniquenessValidator(account_repository, existing_account))
        self.add(AccountBalanceValidator())
