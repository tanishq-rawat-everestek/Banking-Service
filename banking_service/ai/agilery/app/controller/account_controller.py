"""
Account Management API endpoints.
"""

import logging

from fastapi import APIRouter, Depends, Response, status

from ai.agilery.app.dto.account import (
    AccountCreateDto,
    AccountDto,
    AccountPatchDto,
    AccountUpdateDto,
)
from ai.agilery.app.dto.page import PageResponse
from ai.agilery.app.security.jwt import require_permission
from ai.agilery.app.service.account_service import AccountService
from ai.agilery.app.service.service_provider import (
    get_account_service,
    get_account_validator,
)
from ai.agilery.app.validation.service.account_validation_service import (
    AccountValidationService,
)

router = APIRouter(prefix="/accounts", tags=["Accounts"])
logger = logging.getLogger(__name__)


# ======================================================
# POST /accounts — Create
# ======================================================
@router.post(
    "",
    response_model=AccountDto,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("account.create"))],
)
def create(
    dto: AccountCreateDto,
    service: AccountService = Depends(get_account_service),
    validator: AccountValidationService = Depends(get_account_validator),
):
    """Create a new bank account with unique account number, email, and phone number."""
    logger.info("Received request to create account for: %s", dto.email)
    validator.on_create(dto)
    result = service.create(dto)
    logger.info("Account created successfully with ID: %s", result.id)
    return result


# ======================================================
# PUT /accounts/{id} — Full Update
# ======================================================
@router.put(
    "/{id}",
    response_model=AccountDto,
    dependencies=[Depends(require_permission("account.update"))],
)
def update(
    id: int,
    dto: AccountUpdateDto,
    service: AccountService = Depends(get_account_service),
    validator: AccountValidationService = Depends(get_account_validator),
):
    """Update an existing bank account."""
    logger.info("Received PUT request for account ID: %s", id)
    dto.id = id
    validator.on_update(dto)
    result = service.update(id, dto)
    logger.info("Account ID: %s updated successfully.", id)
    return result


# ======================================================
# PATCH /accounts/{id} — Partial Update
# ======================================================
@router.patch(
    "/{id}",
    response_model=AccountDto,
    dependencies=[Depends(require_permission("account.update"))],
)
def patch(
    id: int,
    dto: AccountPatchDto,
    service: AccountService = Depends(get_account_service),
    validator: AccountValidationService = Depends(get_account_validator),
):
    """Partially update an existing bank account."""
    logger.info("Received PATCH request for account ID: %s", id)
    dto.id = id
    validator.on_patch(dto)
    result = service.patch(id, dto)
    logger.info("Account ID: %s patched successfully.", id)
    return result


# ======================================================
# GET /accounts/{id} — Get by ID
# ======================================================
@router.get(
    "/{id}",
    response_model=AccountDto,
    dependencies=[Depends(require_permission("account.view"))],
)
def get(
    id: int,
    service: AccountService = Depends(get_account_service),
    validator: AccountValidationService = Depends(get_account_validator),
):
    """Retrieve a specific bank account by its ID."""
    logger.info("Received GET request for account ID: %s", id)
    validator.on_get(id)
    result = service.get(id)
    logger.info("Account ID: %s retrieved successfully.", id)
    return result


# ======================================================
# GET /accounts — Get All (Paginated)
# ======================================================
@router.get(
    "",
    response_model=PageResponse[AccountDto],
    dependencies=[Depends(require_permission("account.view"))],
)
def get_all(
    page: int = 0,
    size: int = 20,
    sort: str | None = None,
    service: AccountService = Depends(get_account_service),
    validator: AccountValidationService = Depends(get_account_validator),
):
    """Retrieve a paginated list of all bank accounts."""
    logger.info("Received GET ALL request: page=%s size=%s sort=%s", page, size, sort)
    validator.on_get_all(page, size, sort)
    return service.get_all(page, size, sort)


# ======================================================
# DELETE /accounts/{id} — Delete
# ======================================================
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(require_permission("account.delete"))],
)
def delete(
    id: int,
    service: AccountService = Depends(get_account_service),
    validator: AccountValidationService = Depends(get_account_validator),
):
    """Soft delete a bank account."""
    logger.info("Received DELETE request for account ID: %s", id)
    validator.on_delete(id)
    service.delete(id)
    logger.info("Account ID: %s deleted successfully.", id)
