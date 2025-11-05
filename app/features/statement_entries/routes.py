"""
API routes for Bank Statement Entries
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db.models import TransactionType
from app.core.db.session import get_db

from .schemas import (
    BankStatementEntryCreateRequest,
    BankStatementEntryListResponse,
    BankStatementEntryResponse,
    BankStatementEntryUpdateRequest,
)
from .service import BankStatementEntryService

router = APIRouter(prefix="/api/v1/statement-entries", tags=["Statement Entries"])


@router.post(
    "",
    response_model=BankStatementEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bank statement entry",
)
def create_entry(
    data: BankStatementEntryCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new bank statement entry.

    - **bank_statement_file_id**: Bank statement file ID
    - **bank_account_id**: Bank account ID
    - **category_id**: Category ID for categorization (optional)
    - **tags_csv**: Free-form tags (optional)
    - **date**: Transaction date
    - **time**: Transaction time (optional)
    - **description**: Transaction description
    - **transaction_reference**: Transaction reference number (optional)
    - **debit_credit**: Transaction type (debit/credit)
    - **amount**: Transaction amount
    - **balance**: Account balance after transaction (optional)
    - **notes**: Additional notes (optional)
    - **modified_by**: User who last modified this entry (optional)
    """
    return BankStatementEntryService.create_entry(db, data)


@router.get(
    "/{entry_id}",
    response_model=BankStatementEntryResponse,
    summary="Get a bank statement entry by ID",
)
def get_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get details of a specific bank statement entry by ID.
    """
    return BankStatementEntryService.get_entry(db, entry_id)


@router.get(
    "",
    response_model=BankStatementEntryListResponse,
    summary="Get paginated list of bank statement entries",
)
def get_entries(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    bank_account_id: Optional[UUID] = Query(
        None, description="Filter by bank account ID"
    ),
    bank_statement_file_id: Optional[UUID] = Query(
        None, description="Filter by statement file ID"
    ),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    transaction_type: Optional[TransactionType] = Query(
        None, description="Filter by transaction type (debit/credit)"
    ),
    search: Optional[str] = Query(None, description="Search in description and reference"),
    db: Session = Depends(get_db),
):
    """
    Get a paginated list of bank statement entries.

    Supports filtering and search:
    - **bank_account_id**: Filter by bank account
    - **bank_statement_file_id**: Filter by statement file
    - **category_id**: Filter by category
    - **transaction_type**: Filter by debit or credit
    - **search**: Search in description and transaction reference
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    """
    return BankStatementEntryService.get_entries(
        db,
        page=page,
        page_size=page_size,
        bank_account_id=bank_account_id,
        bank_statement_file_id=bank_statement_file_id,
        category_id=category_id,
        transaction_type=transaction_type,
        search=search,
    )


@router.put(
    "/{entry_id}",
    response_model=BankStatementEntryResponse,
    summary="Update a bank statement entry",
)
def update_entry(
    entry_id: UUID,
    data: BankStatementEntryUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    Update a bank statement entry.

    Only provided fields will be updated (partial update supported).
    """
    return BankStatementEntryService.update_entry(db, entry_id, data)


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a bank statement entry",
)
def delete_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a bank statement entry (hard delete).

    This will also delete all associated entry splits due to cascade delete.
    """
    BankStatementEntryService.delete_entry(db, entry_id)
