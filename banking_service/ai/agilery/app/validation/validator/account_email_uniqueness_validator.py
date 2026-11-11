from typing import Optional

from ai.agilery.app.validation.base.validation_handler import ValidationHandler
from ai.agilery.app.dto.error import ValidationErrorDto
from ai.agilery.app.dto.account import AccountCreateDto, AccountUpdateDto
from ai.agilery.app.entity.account import Account
from ai.agilery.app.repositories.account_repository import AccountRepository


class AccountEmailUniquenessValidator(
    ValidationHandler[AccountCreateDto | AccountUpdateDto]
):
    """Validates that email is unique across all accounts."""

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

        duplicate = self.account_repository.get_by_email(dto.email)

        if duplicate and not duplicate.is_deleted:
            # For updates, allow the same email if it belongs to the same account
            if (
                self.existing_account is None
                or duplicate.id != self.existing_account.id
            ):
                errors.append(
                    ValidationErrorDto(
                        object_name="accountDto",
                        field="email",
                        message=f"Email '{dto.email}' is already in use.",
                    )
                )

        return errors
