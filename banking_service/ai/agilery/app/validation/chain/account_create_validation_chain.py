from ai.agilery.app.validation.base.abstract_validation_chain import (
    AbstractValidationChain,
)
from ai.agilery.app.dto.account import AccountCreateDto
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


class AccountCreateValidationChain(AbstractValidationChain[AccountCreateDto]):
    """Validation chain for account creation.

    Validates business rules for creating a new account including
    uniqueness constraints and balance requirements.
    """

    def __init__(self, account_repository: AccountRepository) -> None:
        super().__init__()
        self.add(AccountNumberUniquenessValidator(account_repository))
        self.add(AccountEmailUniquenessValidator(account_repository))
        self.add(AccountPhoneUniquenessValidator(account_repository))
        self.add(AccountBalanceValidator())
