"""
AccountMapper — maps between AccountDto and Account entity.
"""

from __future__ import annotations

from typing import Any

from ai.agilery.app.entity.account import Account
from ai.agilery.app.dto.account import AccountDto


# pyright: reportIncompatibleVariableOverride=false
# pyright: reportGeneralTypeIssues=false
class AccountMapper:
    """
    Maps AccountDto <-> Account.
    """

    def to_entity(self, dto: Any) -> Account:
        """
        DTO → new Account entity.
        Does NOT set id or audit fields — service handles those.
        """
        account = Account(
            account_number=dto.account_number,
            email=dto.email,
            phone_number=dto.phone_number,
            account_holder_name=dto.account_holder_name,
            balance=dto.balance,
        )
        return account

    def to_dto(self, entity: Account) -> AccountDto:
        """
        Entity → DTO response.
        """
        return AccountDto(
            id=entity.id,
            account_number=entity.account_number,
            email=entity.email,
            phone_number=entity.phone_number,
            account_holder_name=entity.account_holder_name,
            balance=entity.balance,
            created_date_time=entity.created_date_time,
            last_modified_date_time=entity.last_modified_date_time,
            created_by=entity.created_by,
            modified_by=entity.modified_by,
        )

    def to_entity_list(self, dto: list[Any]) -> list[Account]:
        return [self.to_entity(d) for d in dto]

    def to_dto_list(self, entity: list[Account]) -> list[AccountDto]:
        return [self.to_dto(e) for e in entity]

    def update(self, entity: Account, dto: Any) -> None:
        """
        PUT — full update.
        """
        entity.account_number = dto.account_number
        entity.email = dto.email
        entity.phone_number = dto.phone_number
        entity.account_holder_name = dto.account_holder_name
        entity.balance = dto.balance

    def patch(self, entity: Account, dto: Any) -> None:
        """
        PATCH — partial update.
        """
        data = dto.model_dump(exclude_unset=True)

        if "account_number" in data:
            entity.account_number = data["account_number"]
        if "email" in data:
            entity.email = data["email"]
        if "phone_number" in data:
            entity.phone_number = data["phone_number"]
        if "account_holder_name" in data:
            entity.account_holder_name = data["account_holder_name"]
        if "balance" in data:
            entity.balance = data["balance"]


# Module-level singleton — import this everywhere
account_mapper = AccountMapper()
