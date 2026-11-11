"""
Transaction database model.
"""

# pyright: reportIncompatibleVariableOverride=false
from datetime import datetime
from decimal import Decimal
from typing import ClassVar, Optional, TYPE_CHECKING

from sqlalchemy import Column, Index, Numeric, String, DateTime, Boolean, text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from ai.agilery.app.entity.account import Account


class Transaction(SQLModel, table=True):
    """
    Transaction entity mapped to database table `transactions`.
    """

    __tablename__: ClassVar[str] = "transactions"

    __table_args__ = (
        Index("idx_transaction_transaction_id", "transaction_id"),
        Index("idx_transaction_from_account_id", "from_account_id"),
        Index("idx_transaction_to_account_id", "to_account_id"),
        Index("idx_transaction_transaction_type", "transaction_type"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    transaction_id: str = Field(
        sa_column=Column("transaction_id", String(50), nullable=False, unique=True),
    )

    from_account_id: int = Field(foreign_key="accounts.id", nullable=False)
    from_account: "Account" = Relationship(
        back_populates="outgoing_transactions",
        sa_relationship_kwargs={
            "foreign_keys": "[Transaction.from_account_id]",
        },
    )

    to_account_id: int = Field(foreign_key="accounts.id", nullable=False)
    to_account: "Account" = Relationship(
        back_populates="incoming_transactions",
        sa_relationship_kwargs={
            "foreign_keys": "[Transaction.to_account_id]",
        },
    )

    amount: Decimal = Field(
        sa_column=Column("amount", Numeric(precision=15, scale=2), nullable=False),
    )

    transaction_type: str = Field(
        sa_column=Column("transaction_type", String(50), nullable=False),
    )

    description: Optional[str] = Field(
        default=None,
        sa_column=Column("description", String(500), nullable=True),
    )

    # Audit fields
    created_date_time: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column("created_date_time", DateTime, nullable=False),
    )
    last_modified_date_time: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            "last_modified_date_time",
            DateTime,
            nullable=False,
            onupdate=datetime.utcnow,
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
