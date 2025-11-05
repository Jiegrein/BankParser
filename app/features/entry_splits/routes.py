"""
API routes for Bank Statement Entry Splits
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db

from .schemas import (
    EntrySplitCreateRequest,
    EntrySplitListResponse,
    EntrySplitResponse,
    EntrySplitUpdateRequest,
)
from .service import EntrySplitService

router = APIRouter(prefix="/api/v1/entry-splits", tags=["Entry Splits"])


@router.post(
    "",
    response_model=EntrySplitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new entry split",
)
def create_split(
    data: EntrySplitCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new bank statement entry split.

    Used for splitting a single transaction across multiple categories.

    - **bank_statement_entry_id**: Bank statement entry ID
    - **category_id**: Category ID for this split
    - **amount**: Split amount
    - **description**: Split description (optional)
    - **modified_by**: User who created this split (optional)
    """
    return EntrySplitService.create_split(db, data)


@router.get(
    "/{split_id}",
    response_model=EntrySplitResponse,
    summary="Get an entry split by ID",
)
def get_split(
    split_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get details of a specific entry split by ID.
    """
    return EntrySplitService.get_split(db, split_id)


@router.get(
    "",
    response_model=EntrySplitListResponse,
    summary="Get paginated list of entry splits",
)
def get_splits(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    bank_statement_entry_id: Optional[UUID] = Query(
        None, description="Filter by bank statement entry ID"
    ),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db),
):
    """
    Get a paginated list of entry splits.

    Supports filtering:
    - **bank_statement_entry_id**: Filter by bank statement entry
    - **category_id**: Filter by category
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    """
    return EntrySplitService.get_splits(
        db,
        page=page,
        page_size=page_size,
        bank_statement_entry_id=bank_statement_entry_id,
        category_id=category_id,
    )


@router.put(
    "/{split_id}",
    response_model=EntrySplitResponse,
    summary="Update an entry split",
)
def update_split(
    split_id: UUID,
    data: EntrySplitUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    Update an entry split.

    Only provided fields will be updated (partial update supported).
    """
    return EntrySplitService.update_split(db, split_id, data)


@router.delete(
    "/{split_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an entry split",
)
def delete_split(
    split_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete an entry split (hard delete).
    """
    EntrySplitService.delete_split(db, split_id)
