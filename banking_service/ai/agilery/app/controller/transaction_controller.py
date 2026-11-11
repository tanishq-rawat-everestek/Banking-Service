"""
Transaction Management API endpoints.
"""

import logging

from fastapi import APIRouter, Depends, Response, status

from ai.agilery.app.dto.transaction import (
    TransactionCreateDto,
    TransactionDto,
    TransactionPatchDto,
    TransactionUpdateDto,
)
from ai.agilery.app.dto.page import PageResponse
from ai.agilery.app.security.jwt import require_permission
from ai.agilery.app.service.transaction_service import TransactionService
from ai.agilery.app.service.service_provider import (
    get_transaction_service,
    get_transaction_validator,
)
from ai.agilery.app.validation.service.transaction_validation_service import (
    TransactionValidationService,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])
logger = logging.getLogger(__name__)


# ======================================================
# POST /transactions — Create
# ======================================================
@router.post(
    "",
    response_model=TransactionDto,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("transaction.create"))],
)
def create(
    dto: TransactionCreateDto,
    service: TransactionService = Depends(get_transaction_service),
    validator: TransactionValidationService = Depends(get_transaction_validator),
):
    """Create a new transaction between two existing bank accounts."""
    logger.info("Received request to create transaction: %s", dto.transaction_id)
    validator.on_create(dto)
    result = service.create(dto)
    logger.info("Transaction created successfully with ID: %s", result.id)
    return result


# ======================================================
# PUT /transactions/{id} — Full Update
# ======================================================
@router.put(
    "/{id}",
    response_model=TransactionDto,
    dependencies=[Depends(require_permission("transaction.update"))],
)
def update(
    id: int,
    dto: TransactionUpdateDto,
    service: TransactionService = Depends(get_transaction_service),
    validator: TransactionValidationService = Depends(get_transaction_validator),
):
    """Update an existing transaction."""
    logger.info("Received PUT request for transaction ID: %s", id)
    dto.id = id
    validator.on_update(dto)
    result = service.update(id, dto)
    logger.info("Transaction ID: %s updated successfully.", id)
    return result


# ======================================================
# PATCH /transactions/{id} — Partial Update
# ======================================================
@router.patch(
    "/{id}",
    response_model=TransactionDto,
    dependencies=[Depends(require_permission("transaction.update"))],
)
def patch(
    id: int,
    dto: TransactionPatchDto,
    service: TransactionService = Depends(get_transaction_service),
    validator: TransactionValidationService = Depends(get_transaction_validator),
):
    """Partially update an existing transaction."""
    logger.info("Received PATCH request for transaction ID: %s", id)
    dto.id = id
    validator.on_patch(dto)
    result = service.patch(id, dto)
    logger.info("Transaction ID: %s patched successfully.", id)
    return result


# ======================================================
# GET /transactions/{id} — Get by ID
# ======================================================
@router.get(
    "/{id}",
    response_model=TransactionDto,
    dependencies=[Depends(require_permission("transaction.view"))],
)
def get(
    id: int,
    service: TransactionService = Depends(get_transaction_service),
    validator: TransactionValidationService = Depends(get_transaction_validator),
):
    """Retrieve a specific transaction by its ID."""
    logger.info("Received GET request for transaction ID: %s", id)
    validator.on_get(id)
    result = service.get(id)
    logger.info("Transaction ID: %s retrieved successfully.", id)
    return result


# ======================================================
# GET /transactions — Get All (Paginated)
# ======================================================
@router.get(
    "",
    response_model=PageResponse[TransactionDto],
    dependencies=[Depends(require_permission("transaction.view"))],
)
def get_all(
    page: int = 0,
    size: int = 20,
    sort: str | None = None,
    service: TransactionService = Depends(get_transaction_service),
    validator: TransactionValidationService = Depends(get_transaction_validator),
):
    """Retrieve a paginated list of all transactions."""
    logger.info("Received GET ALL request: page=%s size=%s sort=%s", page, size, sort)
    validator.on_get_all(page, size, sort)
    return service.get_all(page, size, sort)


# ======================================================
# DELETE /transactions/{id} — Delete
# ======================================================
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(require_permission("transaction.delete"))],
)
def delete(
    id: int,
    service: TransactionService = Depends(get_transaction_service),
    validator: TransactionValidationService = Depends(get_transaction_validator),
):
    """Soft delete a transaction."""
    logger.info("Received DELETE request for transaction ID: %s", id)
    validator.on_delete(id)
    service.delete(id)
    logger.info("Transaction ID: %s deleted successfully.", id)
