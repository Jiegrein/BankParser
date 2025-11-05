"""
API routes for Bank Statement Files
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db

from .schemas import (
    BankStatementFileCreateRequest,
    BankStatementFileListResponse,
    BankStatementFileResponse,
    BankStatementFileUpdateRequest,
)
from .service import BankStatementFileService

router = APIRouter(prefix="/api/v1/statement-files", tags=["Statement Files"])


@router.post(
    "",
    response_model=BankStatementFileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bank statement file",
)
def create_statement_file(
    data: BankStatementFileCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new bank statement file.

    - **bank_account_id**: Bank account ID this statement belongs to
    - **file_path**: Azure Blob Storage URL
    - **period_start**: Statement period start date
    - **period_end**: Statement period end date
    - **uploaded_by**: User who uploaded this file
    """
    return BankStatementFileService.create_statement_file(db, data)


@router.get(
    "/{statement_file_id}",
    response_model=BankStatementFileResponse,
    summary="Get a bank statement file by ID",
)
def get_statement_file(
    statement_file_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get details of a specific bank statement file by ID.
    """
    return BankStatementFileService.get_statement_file(db, statement_file_id)


@router.get(
    "",
    response_model=BankStatementFileListResponse,
    summary="Get paginated list of bank statement files",
)
def get_statement_files(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    bank_account_id: Optional[UUID] = Query(
        None, description="Filter by bank account ID"
    ),
    search: Optional[str] = Query(None, description="Search in file_path"),
    db: Session = Depends(get_db),
):
    """
    Get a paginated list of bank statement files.

    Supports filtering and search:
    - **bank_account_id**: Filter by bank account
    - **search**: Search in file_path
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    """
    return BankStatementFileService.get_statement_files(
        db,
        page=page,
        page_size=page_size,
        bank_account_id=bank_account_id,
        search=search,
    )


@router.put(
    "/{statement_file_id}",
    response_model=BankStatementFileResponse,
    summary="Update a bank statement file",
)
def update_statement_file(
    statement_file_id: UUID,
    data: BankStatementFileUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    Update a bank statement file.

    Only provided fields will be updated (partial update supported).
    """
    return BankStatementFileService.update_statement_file(db, statement_file_id, data)


@router.delete(
    "/{statement_file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a bank statement file",
)
def delete_statement_file(
    statement_file_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a bank statement file (hard delete).

    This will also delete all associated statement entries due to cascade delete.
    """
    BankStatementFileService.delete_statement_file(db, statement_file_id)
