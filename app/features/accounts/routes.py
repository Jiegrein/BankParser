"""
Bank Accounts API routes
REST endpoints for bank account management
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from .schemas import (
    BankAccountCreateRequest,
    BankAccountUpdateRequest,
    BankAccountResponse,
    BankAccountListResponse
)
from .service import BankAccountService

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/v1/bank-accounts",
    tags=["Bank Accounts"]
)


@router.post(
    "",
    response_model=BankAccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bank account",
    description="Create a new bank account linked to a project"
)
async def create_bank_account(
    data: BankAccountCreateRequest,
    db: Session = Depends(get_db)
) -> BankAccountResponse:
    """
    Create a new bank account

    - **project_id**: Project UUID this account belongs to (required)
    - **account_number**: Account number, last 4 digits only (required)
    - **bank_name**: Bank name (required)
    - **account_type**: Account type, e.g., checking, savings (required)
    - **color**: Color code for visual display (optional)
    - **position_x**: X coordinate for visual positioning (optional)
    - **position_y**: Y coordinate for visual positioning (optional)
    - **created_by**: User who created this account (required)
    """
    return BankAccountService.create_bank_account(db, data)


@router.get(
    "/{account_id}",
    response_model=BankAccountResponse,
    summary="Get a bank account by ID",
    description="Retrieve a single bank account by its UUID"
)
async def get_bank_account(
    account_id: UUID,
    db: Session = Depends(get_db)
) -> BankAccountResponse:
    """
    Get a single bank account by ID

    - **account_id**: UUID of the bank account
    """
    return BankAccountService.get_bank_account(db, account_id)


@router.get(
    "",
    response_model=BankAccountListResponse,
    summary="Get list of bank accounts",
    description="Retrieve a paginated list of bank accounts with optional filters"
)
async def get_bank_accounts(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    project_id: Optional[UUID] = Query(None, description="Filter by project ID"),
    search: Optional[str] = Query(None, description="Search in bank_name, account_number, or account_type"),
    db: Session = Depends(get_db)
) -> BankAccountListResponse:
    """
    Get paginated list of bank accounts

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **project_id**: Filter by project ID (optional)
    - **search**: Search text for bank_name, account_number, or account_type (optional)
    """
    return BankAccountService.get_bank_accounts(
        db=db,
        page=page,
        page_size=page_size,
        project_id=project_id,
        search=search
    )


@router.put(
    "/{account_id}",
    response_model=BankAccountResponse,
    summary="Update a bank account",
    description="Update an existing bank account (partial updates allowed)"
)
async def update_bank_account(
    account_id: UUID,
    data: BankAccountUpdateRequest,
    db: Session = Depends(get_db)
) -> BankAccountResponse:
    """
    Update an existing bank account

    Only provided fields will be updated (partial update).

    - **account_id**: UUID of the bank account to update
    - **account_number**: New account number (optional)
    - **bank_name**: New bank name (optional)
    - **account_type**: New account type (optional)
    - **color**: New color code (optional)
    - **position_x**: New X coordinate (optional)
    - **position_y**: New Y coordinate (optional)
    - **updated_by**: User who updated this account (optional)
    """
    return BankAccountService.update_bank_account(db, account_id, data)


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a bank account",
    description="Delete a bank account (hard delete)"
)
async def delete_bank_account(
    account_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a bank account

    **Note**: This is a hard delete since BankAccount doesn't have an
    is_activated field. The account will be permanently removed.

    - **account_id**: UUID of the bank account to delete
    """
    BankAccountService.delete_bank_account(db, account_id)
