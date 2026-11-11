"""
Transaction repository — all database access for the Transaction entity.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import Depends
from sqlalchemy import and_, func
from sqlmodel import Session, select, col

from ai.agilery.app.db.session import get_db
from ai.agilery.app.entity.transaction import Transaction


class TransactionRepository:
    """
    Data access layer for Transaction entity.
    """

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    # -------------------------
    # Write
    # -------------------------

    def save(self, entity: Transaction) -> Transaction:
        """Persist a new or modified Transaction. Uses flush, not commit."""
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: Transaction) -> None:
        """Delete a Transaction (soft delete). Uses save."""
        entity.is_deleted = True
        self.save(entity)

    # -------------------------
    # Read — single
    # -------------------------

    def get_by_id(self, id: int) -> Optional[Transaction]:
        """Fetch by primary key — fastest lookup."""
        return self.db.get(Transaction, id)

    def get_by_transaction_id(self, transaction_id: str) -> Optional[Transaction]:
        """Fetch by unique transaction ID."""
        stmt = select(Transaction).where(
            and_(
                col(Transaction.transaction_id) == transaction_id,
                not col(Transaction.is_deleted),
            )
        )
        return self.db.exec(stmt).first()

    # -------------------------
    # Read — collection
    # -------------------------

    def get_by_from_account_id(self, from_account_id: int) -> List[Transaction]:
        """Fetch all transactions from a specific account."""
        stmt = select(Transaction).where(
            and_(
                col(Transaction.from_account_id) == from_account_id,
                not col(Transaction.is_deleted),
            )
        )
        return list(self.db.exec(stmt).all())

    def get_by_to_account_id(self, to_account_id: int) -> List[Transaction]:
        """Fetch all transactions to a specific account."""
        stmt = select(Transaction).where(
            and_(
                col(Transaction.to_account_id) == to_account_id,
                not col(Transaction.is_deleted),
            )
        )
        return list(self.db.exec(stmt).all())

    def get_by_account_id(self, account_id: int) -> List[Transaction]:
        """Fetch all transactions involving a specific account (either from or to)."""
        stmt = select(Transaction).where(
            and_(
                not col(Transaction.is_deleted),
                (col(Transaction.from_account_id) == account_id)
                | (col(Transaction.to_account_id) == account_id),
            )
        )
        return list(self.db.exec(stmt).all())

    def get_by_transaction_type(self, transaction_type: str) -> List[Transaction]:
        """Fetch all transactions by transaction type."""
        stmt = select(Transaction).where(
            and_(
                col(Transaction.transaction_type) == transaction_type,
                not col(Transaction.is_deleted),
            )
        )
        return list(self.db.exec(stmt).all())

    def get_by_date_range(self, start: datetime, end: datetime) -> List[Transaction]:
        """Fetch all transactions created within a date range."""
        stmt = select(Transaction).where(
            and_(
                col(Transaction.created_date_time) >= start,
                col(Transaction.created_date_time) <= end,
                not col(Transaction.is_deleted),
            )
        )
        return list(self.db.exec(stmt).all())

    # -------------------------
    # Pagination
    # -------------------------

    def get_paginated(
        self, offset: int, limit: int, order_by=None
    ) -> List[Transaction]:
        """Fetch paginated transactions."""
        stmt = select(Transaction).where(not col(Transaction.is_deleted))
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.offset(offset).limit(limit)
        return list(self.db.exec(stmt).all())

    def count(self) -> int:
        """Count total non-deleted transactions."""
        stmt = (
            select(func.count())
            .select_from(Transaction)
            .where(not col(Transaction.is_deleted))
        )
        return self.db.exec(stmt).one()
