from typing import Optional

from ai.agilery.app.validation.base.validation_handler import ValidationHandler
from ai.agilery.app.dto.error import ValidationErrorDto
from ai.agilery.app.dto.account import AccountCreateDto, AccountUpdateDto
from ai.agilery.app.entity.account import Account
from ai.agilery.app.repositories.account_repository import AccountRepository


class AccountPhoneUniquenessValidator(
    ValidationHandler[AccountCreateDto | AccountUpdateDto]
):
    """Validates that phone number is unique across all accounts."""

    def __init__(
        self,
        account_repository: AccountRepository,
        existing_account: Optional[Account] = None,
    ):
        self.account_repository = account_repository
        self.existing_account = existing_account

    def validate(
        self, dto: AccountCreateDto | AccountUpdateDto
    ) -> list[ValidationErrorDto]:
        errors: list[ValidationErrorDto] = []

        duplicate = self.account_repository.get_by_phone_number(dto.phone_number)

        if duplicate and not duplicate.is_deleted:
            # For updates, allow the same phone number if it belongs to the same account
            if (
                self.existing_account is None
                or duplicate.id != self.existing_account.id
            ):
                errors.append(
                    ValidationErrorDto(
                        object_name="accountDto",
                        field="phoneNumber",
                        message=f"Phone number '{dto.phone_number}' is already in use.",
                    )
                )

        return errors
