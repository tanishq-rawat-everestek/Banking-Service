"""
TransactionMapper — maps between TransactionDto and Transaction entity.
"""

from __future__ import annotations

from typing import Any

from ai.agilery.app.entity.transaction import Transaction
from ai.agilery.app.dto.transaction import TransactionDto


# pyright: reportIncompatibleVariableOverride=false
# pyright: reportGeneralTypeIssues=false
class TransactionMapper:
    """
    Maps TransactionDto <-> Transaction.
    """

    def to_entity(self, dto: Any) -> Transaction:
        """
        DTO → new Transaction entity.
        Does NOT set id or audit fields — service handles those.
        """
        transaction = Transaction(
            transaction_id=dto.transaction_id,
            from_account_id=dto.from_account_id,
            to_account_id=dto.to_account_id,
            amount=dto.amount,
            transaction_type=dto.transaction_type,
            description=dto.description,
        )
        return transaction

    def to_dto(self, entity: Transaction) -> TransactionDto:
        """
        Entity → DTO response.
        """
        return TransactionDto(
            id=entity.id,
            transaction_id=entity.transaction_id,
            from_account_id=entity.from_account_id,
            to_account_id=entity.to_account_id,
            amount=entity.amount,
            transaction_type=entity.transaction_type,
            description=entity.description,
            created_date_time=entity.created_date_time,
            last_modified_date_time=entity.last_modified_date_time,
            created_by=entity.created_by,
            modified_by=entity.modified_by,
        )

    def to_entity_list(self, dto: list[Any]) -> list[Transaction]:
        return [self.to_entity(d) for d in dto]

    def to_dto_list(self, entity: list[Transaction]) -> list[TransactionDto]:
        return [self.to_dto(e) for e in entity]

    def update(self, entity: Transaction, dto: Any) -> None:
        """
        PUT — full update.
        """
        entity.transaction_id = dto.transaction_id
        entity.from_account_id = dto.from_account_id
        entity.to_account_id = dto.to_account_id
        entity.amount = dto.amount
        entity.transaction_type = dto.transaction_type
        entity.description = dto.description

    def patch(self, entity: Transaction, dto: Any) -> None:
        """
        PATCH — partial update.
        """
        data = dto.model_dump(exclude_unset=True)

        if "transaction_id" in data:
            entity.transaction_id = data["transaction_id"]
        if "from_account_id" in data:
            entity.from_account_id = data["from_account_id"]
        if "to_account_id" in data:
            entity.to_account_id = data["to_account_id"]
        if "amount" in data:
            entity.amount = data["amount"]
        if "transaction_type" in data:
            entity.transaction_type = data["transaction_type"]
        if "description" in data:
            entity.description = data["description"]


# Module-level singleton — import this everywhere
transaction_mapper = TransactionMapper()
