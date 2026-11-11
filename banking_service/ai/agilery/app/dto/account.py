"""
Account schemas.

Exposes separate decoupled schemas for create, update, patch, and response
to avoid static type checking errors with inheritance overrides.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi_camelcase import CamelModel
from pydantic import ConfigDict, EmailStr, Field


class AccountCreateDto(CamelModel):
    """Account request schema for POST (create)."""

    account_number: str = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Unique account number for the bank account",
        json_schema_extra={"example": "ACC123456789"},
    )
    email: EmailStr = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Unique email address of the account holder",
        json_schema_extra={"example": "john.doe@example.com"},
    )
    phone_number: str = Field(
        ...,
        min_length=10,
        max_length=15,
        description="Unique phone number of the account holder",
        json_schema_extra={"example": "1234567890"},
    )
    account_holder_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the account holder",
        json_schema_extra={"example": "John Doe"},
    )
    balance: Decimal = Field(
        ...,
        ge=0,
        description="Current balance in the account",
        json_schema_extra={"example": 1000.0},
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AccountUpdateDto(CamelModel):
    """Account request schema for PUT (full update)."""

    id: Optional[int] = Field(default=None, exclude=True)
    account_number: str = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Unique account number for the bank account",
        json_schema_extra={"example": "ACC123456789"},
    )
    email: EmailStr = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Unique email address of the account holder",
        json_schema_extra={"example": "john.doe@example.com"},
    )
    phone_number: str = Field(
        ...,
        min_length=10,
        max_length=15,
        description="Unique phone number of the account holder",
        json_schema_extra={"example": "1234567890"},
    )
    account_holder_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the account holder",
        json_schema_extra={"example": "John Doe"},
    )
    balance: Decimal = Field(
        ...,
        ge=0,
        description="Current balance in the account",
        json_schema_extra={"example": 1000.0},
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AccountPatchDto(CamelModel):
    """Account request schema for PATCH (partial update). All fields Optional."""

    id: Optional[int] = Field(default=None, exclude=True)
    account_number: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=20,
        description="Unique account number for the bank account",
        json_schema_extra={"example": "ACC123456789"},
    )
    email: Optional[EmailStr] = Field(
        default=None,
        min_length=5,
        max_length=100,
        description="Unique email address of the account holder",
        json_schema_extra={"example": "john.doe@example.com"},
    )
    phone_number: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=15,
        description="Unique phone number of the account holder",
        json_schema_extra={"example": "1234567890"},
    )
    account_holder_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Full name of the account holder",
        json_schema_extra={"example": "John Doe"},
    )
    balance: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description="Current balance in the account",
        json_schema_extra={"example": 1000.0},
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AccountDto(CamelModel):
    """Account response DTO. Includes id, audit fields, response children."""

    id: Optional[int] = Field(
        default=None,
        description="Unique identifier for the account",
        json_schema_extra={"readOnly": True, "example": 1},
    )
    account_number: str = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Unique account number for the bank account",
        json_schema_extra={"example": "ACC123456789"},
    )
    email: EmailStr = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Unique email address of the account holder",
        json_schema_extra={"example": "john.doe@example.com"},
    )
    phone_number: str = Field(
        ...,
        min_length=10,
        max_length=15,
        description="Unique phone number of the account holder",
        json_schema_extra={"example": "1234567890"},
    )
    account_holder_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the account holder",
        json_schema_extra={"example": "John Doe"},
    )
    balance: Decimal = Field(
        ...,
        ge=0,
        description="Current balance in the account",
        json_schema_extra={"example": 1000.0},
    )

    created_date_time: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the account was created",
        json_schema_extra={"readOnly": True, "example": "2024-01-15T10:30:00+00:00"},
    )
    last_modified_date_time: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the account was last modified",
        json_schema_extra={"readOnly": True, "example": "2024-01-15T10:30:00+00:00"},
    )
    created_by: Optional[str] = Field(
        default=None,
        description="User who created the account",
        json_schema_extra={"readOnly": True, "example": "admin"},
    )
    modified_by: Optional[str] = Field(
        default=None,
        description="User who last modified the account",
        json_schema_extra={"readOnly": True, "example": "admin"},
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
