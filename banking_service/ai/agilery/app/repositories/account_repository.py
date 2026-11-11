"""
Account repository — all database access for the Account entity.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import Depends
from sqlalchemy import and_, func
from sqlmodel import Session, select, col

from ai.agilery.app.db.session import get_db
from ai.agilery.app.entity.account import Account


class AccountRepository:
    """
    Data access layer for Account entity.
    """

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    # -------------------------
    # Write
    # -------------------------

    def save(self, entity: Account) -> Account:
        """Persist a new or modified Account. Uses flush, not commit."""
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: Account) -> None:
        """Delete an Account (soft delete). Uses save."""
        entity.is_deleted = True
        self.save(entity)

    # -------------------------
    # Read — single
    # -------------------------

    def get_by_id(self, id: int) -> Optional[Account]:
        """Fetch by primary key — fastest lookup."""
        return self.db.get(Account, id)

    def get_by_id_for_update(self, id: int) -> Optional[Account]:
        """Fetch by primary key with row-level lock (SELECT FOR UPDATE) to prevent race conditions."""
        stmt = select(Account).where(col(Account.id) == id).with_for_update()
        return self.db.exec(stmt).first()

    def get_by_account_number(self, account_number: str) -> Optional[Account]:
        """Fetch by unique account number."""
        stmt = select(Account).where(
            and_(
                col(Account.account_number) == account_number,
                not col(Account.is_deleted),
            )
        )
        return self.db.exec(stmt).first()

    def get_by_email(self, email: str) -> Optional[Account]:
        """Fetch by unique email."""
        stmt = select(Account).where(
            and_(col(Account.email) == email, not col(Account.is_deleted))
        )
        return self.db.exec(stmt).first()

    def get_by_phone_number(self, phone_number: str) -> Optional[Account]:
        """Fetch by unique phone number."""
        stmt = select(Account).where(
            and_(
                col(Account.phone_number) == phone_number,
                not col(Account.is_deleted),
            )
        )
        return self.db.exec(stmt).first()

    # -------------------------
    # Read — collection
    # -------------------------

    def get_by_account_holder_name(self, account_holder_name: str) -> List[Account]:
        """Fetch all accounts by account holder name."""
        stmt = select(Account).where(
            and_(
                col(Account.account_holder_name) == account_holder_name,
                not col(Account.is_deleted),
            )
        )
        return list(self.db.exec(stmt).all())

    def get_by_date_range(self, start: datetime, end: datetime) -> List[Account]:
        """Fetch all accounts created within a date range."""
        stmt = select(Account).where(
            and_(
                col(Account.created_date_time) >= start,
                col(Account.created_date_time) <= end,
                not col(Account.is_deleted),
            )
        )
        return list(self.db.exec(stmt).all())

    # -------------------------
    # Pagination
    # -------------------------

    def get_paginated(self, offset: int, limit: int, order_by=None) -> List[Account]:
        """Fetch paginated accounts."""
        stmt = select(Account).where(not col(Account.is_deleted))
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.offset(offset).limit(limit)
        return list(self.db.exec(stmt).all())

    def count(self) -> int:
        """Count total non-deleted accounts."""
        stmt = (
            select(func.count()).select_from(Account).where(not col(Account.is_deleted))
        )
        return self.db.exec(stmt).one()
