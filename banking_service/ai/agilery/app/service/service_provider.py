"""
Dependency injection providers for services and validation services.

This module provides FastAPI dependency functions that resolve service and validation
service instances using FastAPI's class-based dependency resolution.
"""

from fastapi import Depends

from ai.agilery.app.service.account_service import AccountService
from ai.agilery.app.service.impl.account_service_impl import AccountServiceImpl
from ai.agilery.app.service.transaction_service import TransactionService
from ai.agilery.app.service.impl.transaction_service_impl import TransactionServiceImpl
from ai.agilery.app.validation.service.account_validation_service import (
    AccountValidationService,
)
from ai.agilery.app.validation.service.transaction_validation_service import (
    TransactionValidationService,
)

# ======================================================
# Service Providers
# ======================================================


def get_account_service(service: AccountServiceImpl = Depends()) -> AccountService:
    """
    Provide AccountService instance.

    Args:
        service: AccountServiceImpl instance resolved by FastAPI.

    Returns:
        AccountService: The service instance.
    """
    return service


def get_transaction_service(
    service: TransactionServiceImpl = Depends(),
) -> TransactionService:
    """
    Provide TransactionService instance.

    Args:
        service: TransactionServiceImpl instance resolved by FastAPI.

    Returns:
        TransactionService: The service instance.
    """
    return service


# ======================================================
# Validation Service Providers
# ======================================================


def get_account_validator(
    validator: AccountValidationService = Depends(),
) -> AccountValidationService:
    """
    Provide AccountValidationService instance.

    Args:
        validator: AccountValidationService instance resolved by FastAPI.

    Returns:
        AccountValidationService: The validation service instance.
    """
    return validator


def get_transaction_validator(
    validator: TransactionValidationService = Depends(),
) -> TransactionValidationService:
    """
    Provide TransactionValidationService instance.

    Args:
        validator: TransactionValidationService instance resolved by FastAPI.

    Returns:
        TransactionValidationService: The validation service instance.
    """
    return validator
