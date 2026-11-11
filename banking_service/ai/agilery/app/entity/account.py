"""
Account database model.
"""

# pyright: reportIncompatibleVariableOverride=false
from datetime import datetime, timezone
from decimal import Decimal
from typing import ClassVar, List, Optional, TYPE_CHECKING

from sqlalchemy import Column, Index, Numeric, String, DateTime, Boolean, text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from ai.agilery.app.entity.transaction import Transaction


class Account(SQLModel, table=True):
    """
    Account entity mapped to database table `accounts`.
    """

    __tablename__: ClassVar[str] = "accounts"

    __table_args__ = (
        Index("idx_account_account_number", "account_number"),
        Index("idx_account_email", "email"),
        Index("idx_account_phone_number", "phone_number"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    account_number: str = Field(
        sa_column=Column("account_number", String(20), nullable=False, unique=True),
    )

    email: str = Field(
        sa_column=Column("email", String(100), nullable=False, unique=True),
    )

    phone_number: str = Field(
        sa_column=Column("phone_number", String(15), nullable=False, unique=True),
    )

    account_holder_name: str = Field(
        sa_column=Column("account_holder_name", String(100), nullable=False),
    )

    balance: Decimal = Field(
        sa_column=Column("balance", Numeric(precision=15, scale=2), nullable=False),
    )

    # One-to-many relationship with transactions (from account)
    outgoing_transactions: List["Transaction"] = Relationship(
        back_populates="from_account",
        sa_relationship_kwargs={
            "foreign_keys": "[Transaction.from_account_id]",
        },
    )

    # One-to-many relationship with transactions (to account)
    incoming_transactions: List["Transaction"] = Relationship(
        back_populates="to_account",
        sa_relationship_kwargs={
            "foreign_keys": "[Transaction.to_account_id]",
        },
    )

    # Audit fields
    created_date_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("created_date_time", DateTime, nullable=False),
    )
    last_modified_date_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            "last_modified_date_time",
            DateTime,
            nullable=False,
            onupdate=lambda: datetime.now(timezone.utc),
        ),
    )
    created_by: Optional[str] = Field(default=None)
    modified_by: Optional[str] = Field(default=None)

    is_deleted: bool = Field(
        default=False,
        sa_column=Column(
            "is_deleted", Boolean, nullable=False, server_default=text("0")
        ),
    )
