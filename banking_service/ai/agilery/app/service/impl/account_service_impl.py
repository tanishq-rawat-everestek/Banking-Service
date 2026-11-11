"""
Account Service Implementation.
"""

import logging

from fastapi import Depends
from sqlalchemy import asc, desc
from sqlmodel import col

from ai.agilery.app.dto.account import (
    AccountCreateDto,
    AccountDto,
    AccountPatchDto,
    AccountUpdateDto,
)
from ai.agilery.app.dto.page import PageInfo, PageResponse
from ai.agilery.app.entity.account import Account
from ai.agilery.app.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)
from ai.agilery.app.exception.validation_exception import ValidationException
from ai.agilery.app.mapper.account_mapper import account_mapper
from ai.agilery.app.repositories.account_repository import AccountRepository
from ai.agilery.app.security.jwt import get_current_user
from ai.agilery.app.service.account_service import AccountService
from ai.agilery.app.util.audit import apply_created_audit, apply_modified_audit

logger = logging.getLogger(__name__)


class AccountServiceImpl(AccountService):
    """
    Implementation of AccountService.
    """

    def __init__(
        self,
        account_repo: AccountRepository = Depends(),
        user: dict = Depends(get_current_user),
    ):
        self.account_repo = account_repo
        self.current_user = user

    # -----------------------------------------------
    # Helpers
    # -----------------------------------------------

    def _parse_sort(self, sort: str | None):
        """
        Parse sort parameter into SQLAlchemy order_by expression.

        Args:
            sort: Sort string in format 'field,direction'

        Returns:
            SQLAlchemy order_by expression or None
        """
        if not sort:
            return None
        try:
            field, direction = sort.split(",")
        except ValueError:
            raise ValidationException(
                description="Invalid sort format. Expected 'field,asc|desc'"
            )

        allowed_fields = {
            "createdDateTime": Account.created_date_time,
            "lastModifiedDateTime": Account.last_modified_date_time,
            "accountNumber": Account.account_number,
            "email": Account.email,
            "accountHolderName": Account.account_holder_name,
            "balance": Account.balance,
        }

        if field not in allowed_fields:
            raise ValidationException(description=f"Invalid sort field: {field}")
        if direction not in {"asc", "desc"}:
            raise ValidationException(
                description=f"Invalid sort direction: {direction}"
            )

        return (
            asc(col(allowed_fields[field]))
            if direction == "asc"
            else desc(col(allowed_fields[field]))
        )

    # -----------------------------------------------
    # CRUD Operations
    # -----------------------------------------------

    def create(self, dto: AccountCreateDto) -> AccountDto:
        """
        Create a new account.

        Args:
            dto: Account creation data

        Returns:
            Created account DTO
        """
        logger.info("Creating account with account number: %s", dto.account_number)

        # Check uniqueness constraints
        existing_by_account_number = self.account_repo.get_by_account_number(
            dto.account_number
        )
        if existing_by_account_number and not existing_by_account_number.is_deleted:
            raise ValidationException(
                description=f"Account with account number '{dto.account_number}' already exists."
            )

        existing_by_email = self.account_repo.get_by_email(dto.email)
        if existing_by_email and not existing_by_email.is_deleted:
            raise ValidationException(
                description=f"Account with email '{dto.email}' already exists."
            )

        existing_by_phone = self.account_repo.get_by_phone_number(dto.phone_number)
        if existing_by_phone and not existing_by_phone.is_deleted:
            raise ValidationException(
                description=f"Account with phone number '{dto.phone_number}' already exists."
            )

        entity = account_mapper.to_entity(dto)
        apply_created_audit(entity, self.current_user)
        entity = self.account_repo.save(entity)
        logger.info("Account created with ID: %s", entity.id)
        return account_mapper.to_dto(entity)

    def get(self, account_id: int) -> AccountDto:
        """
        Retrieve an account by ID.

        Args:
            account_id: ID of the account

        Returns:
            Account DTO
        """
        existing = self.account_repo.get_by_id(account_id)
        if not existing or existing.is_deleted:
            raise ResourceNotFoundException(
                f"Account with ID '{account_id}' not found."
            )
        return account_mapper.to_dto(existing)

    def get_all(self, page: int, size: int, sort: str | None) -> PageResponse:
        """
        Retrieve all accounts with pagination and sorting.

        Args:
            page: Page number (0-indexed)
            size: Page size
            sort: Sort specification

        Returns:
            Paginated response containing account DTOs
        """
        order_by = self._parse_sort(sort)
        offset = page * size
        items = self.account_repo.get_paginated(
            offset=offset, limit=size, order_by=order_by
        )
        total = self.account_repo.count()
        total_pages = (total + size - 1) // size if size > 0 else 0

        return PageResponse(
            content=[account_mapper.to_dto(account) for account in items],
            page=PageInfo(
                size=size,
                number=page,
                total_elements=total,
                total_pages=total_pages,
            ),
        )

    def update(self, account_id: int, dto: AccountUpdateDto) -> AccountDto:
        """
        Update an existing account.

        Args:
            account_id: ID of the account to update
            dto: Account update data

        Returns:
            Updated account DTO
        """
        logger.info("Updating account with ID: %s", account_id)
        existing = self.account_repo.get_by_id(account_id)
        if not existing or existing.is_deleted:
            raise ResourceNotFoundException(
                f"Account with ID '{account_id}' not found."
            )

        # Check uniqueness constraints if fields are being changed
        if dto.account_number != existing.account_number:
            existing_by_account_number = self.account_repo.get_by_account_number(
                dto.account_number
            )
            if existing_by_account_number and not existing_by_account_number.is_deleted:
                raise ValidationException(
                    description=f"Account with account number '{dto.account_number}' already exists."
                )

        if dto.email != existing.email:
            existing_by_email = self.account_repo.get_by_email(dto.email)
            if existing_by_email and not existing_by_email.is_deleted:
                raise ValidationException(
                    description=f"Account with email '{dto.email}' already exists."
                )

        if dto.phone_number != existing.phone_number:
            existing_by_phone = self.account_repo.get_by_phone_number(dto.phone_number)
            if existing_by_phone and not existing_by_phone.is_deleted:
                raise ValidationException(
                    description=f"Account with phone number '{dto.phone_number}' already exists."
                )

        account_mapper.update(existing, dto)
        apply_modified_audit(existing, self.current_user)
        existing = self.account_repo.save(existing)
        logger.info("Account with ID '%s' updated.", account_id)
        return account_mapper.to_dto(existing)

    def patch(self, account_id: int, dto: AccountPatchDto) -> AccountDto:
        """
        Partially update an existing account.

        Args:
            account_id: ID of the account to patch
            dto: Account patch data

        Returns:
            Patched account DTO
        """
        logger.info("Patching account with ID: %s", account_id)
        existing = self.account_repo.get_by_id(account_id)
        if not existing or existing.is_deleted:
            raise ResourceNotFoundException(
                f"Account with ID '{account_id}' not found."
            )

        # Check uniqueness constraints for fields being changed
        if (
            dto.account_number is not None
            and dto.account_number != existing.account_number
        ):
            existing_by_account_number = self.account_repo.get_by_account_number(
                dto.account_number
            )
            if existing_by_account_number and not existing_by_account_number.is_deleted:
                raise ValidationException(
                    description=f"Account with account number '{dto.account_number}' already exists."
                )

        if dto.email is not None and dto.email != existing.email:
            existing_by_email = self.account_repo.get_by_email(dto.email)
            if existing_by_email and not existing_by_email.is_deleted:
                raise ValidationException(
                    description=f"Account with email '{dto.email}' already exists."
                )

        if dto.phone_number is not None and dto.phone_number != existing.phone_number:
            existing_by_phone = self.account_repo.get_by_phone_number(dto.phone_number)
            if existing_by_phone and not existing_by_phone.is_deleted:
                raise ValidationException(
                    description=f"Account with phone number '{dto.phone_number}' already exists."
                )

        account_mapper.patch(existing, dto)
        apply_modified_audit(existing, self.current_user)
        existing = self.account_repo.save(existing)
        logger.info("Account with ID '%s' patched.", account_id)
        return account_mapper.to_dto(existing)

    def delete(self, account_id: int) -> None:
        """
        Soft delete an account.

        Args:
            account_id: ID of the account to delete
        """
        logger.info("Deleting account with ID: %s", account_id)
        existing = self.account_repo.get_by_id(account_id)
        if not existing or existing.is_deleted:
            raise ResourceNotFoundException(
                f"Account with ID '{account_id}' not found."
            )

        # Soft delete: set is_deleted flag
        existing.is_deleted = True
        apply_modified_audit(existing, self.current_user)
        self.account_repo.save(existing)
        logger.info("Account with ID '%s' soft-deleted.", account_id)
