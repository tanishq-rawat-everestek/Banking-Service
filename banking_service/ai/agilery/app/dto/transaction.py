"""
Transaction schemas.

Exposes separate decoupled schemas for create, update, patch, and response
to avoid static type checking errors with inheritance overrides.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi_camelcase import CamelModel
from pydantic import ConfigDict, Field


class TransactionCreateDto(CamelModel):
    """Transaction request schema for POST (create)."""

    transaction_id: str = Field(
        ...,
        min_length=10,
        max_length=50,
        description="Unique transaction identifier",
        json_schema_extra={"example": "TXN1234567890"},
    )
    from_account_id: int = Field(
        ...,
        ge=1,
        description="ID of the account from which money is transferred",
        json_schema_extra={"example": 1},
    )
    to_account_id: int = Field(
        ...,
        ge=1,
        description="ID of the account to which money is transferred",
        json_schema_extra={"example": 2},
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        description="Amount to be transferred",
        json_schema_extra={"example": 500.0},
    )
    transaction_type: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Type of transaction",
        json_schema_extra={"example": "TRANSFER"},
    )
    description: Optional[str] = Field(
        default=None,
        min_length=0,
        max_length=500,
        description="Optional description of the transaction",
        json_schema_extra={"example": "Payment for services"},
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TransactionUpdateDto(CamelModel):
    """Transaction request schema for PUT (full update)."""

    id: Optional[int] = Field(default=None, exclude=True)
    transaction_id: str = Field(
        ...,
        min_length=10,
        max_length=50,
        description="Unique transaction identifier",
        json_schema_extra={"example": "TXN1234567890"},
    )
    from_account_id: int = Field(
        ...,
        ge=1,
        description="ID of the account from which money is transferred",
        json_schema_extra={"example": 1},
    )
    to_account_id: int = Field(
        ...,
        ge=1,
        description="ID of the account to which money is transferred",
        json_schema_extra={"example": 2},
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        description="Amount to be transferred",
        json_schema_extra={"example": 500.0},
    )
    transaction_type: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Type of transaction",
        json_schema_extra={"example": "TRANSFER"},
    )
    description: Optional[str] = Field(
        default=None,
        min_length=0,
        max_length=500,
        description="Optional description of the transaction",
        json_schema_extra={"example": "Payment for services"},
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TransactionPatchDto(CamelModel):
    """Transaction request schema for PATCH (partial update). All fields Optional."""

    id: Optional[int] = Field(default=None, exclude=True)
    transaction_id: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=50,
        description="Unique transaction identifier",
        json_schema_extra={"example": "TXN1234567890"},
    )
    from_account_id: Optional[int] = Field(
        default=None,
        ge=1,
        description="ID of the account from which money is transferred",
        json_schema_extra={"example": 1},
    )
    to_account_id: Optional[int] = Field(
        default=None,
        ge=1,
        description="ID of the account to which money is transferred",
        json_schema_extra={"example": 2},
    )
    amount: Optional[Decimal] = Field(
        default=None,
        gt=0,
        description="Amount to be transferred",
        json_schema_extra={"example": 500.0},
    )
    transaction_type: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="Type of transaction",
        json_schema_extra={"example": "TRANSFER"},
    )
    description: Optional[str] = Field(
        default=None,
        min_length=0,
        max_length=500,
        description="Optional description of the transaction",
        json_schema_extra={"example": "Payment for services"},
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TransactionDto(CamelModel):
    """Transaction response DTO. Includes id, audit fields, response children."""

    id: Optional[int] = Field(
        default=None,
        description="Unique identifier for the transaction",
        json_schema_extra={"readOnly": True, "example": 1},
    )
    transaction_id: str = Field(
        ...,
        min_length=10,
        max_length=50,
        description="Unique transaction identifier",
        json_schema_extra={"example": "TXN1234567890"},
    )
    from_account_id: int = Field(
        ...,
        ge=1,
        description="ID of the account from which money is transferred",
        json_schema_extra={"example": 1},
    )
    to_account_id: int = Field(
        ...,
        ge=1,
        description="ID of the account to which money is transferred",
        json_schema_extra={"example": 2},
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        description="Amount to be transferred",
        json_schema_extra={"example": 500.0},
    )
    transaction_type: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Type of transaction",
        json_schema_extra={"example": "TRANSFER"},
    )
    description: Optional[str] = Field(
        default=None,
        min_length=0,
        max_length=500,
        description="Optional description of the transaction",
        json_schema_extra={"example": "Payment for services"},
    )

    created_date_time: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the transaction was created",
        json_schema_extra={"readOnly": True, "example": "2024-01-15T10:30:00+00:00"},
    )
    last_modified_date_time: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the transaction was last modified",
        json_schema_extra={"readOnly": True, "example": "2024-01-15T10:30:00+00:00"},
    )
    created_by: Optional[str] = Field(
        default=None,
        description="User who created the transaction",
        json_schema_extra={"readOnly": True, "example": "admin"},
    )
    modified_by: Optional[str] = Field(
        default=None,
        description="User who last modified the transaction",
        json_schema_extra={"readOnly": True, "example": "admin"},
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
