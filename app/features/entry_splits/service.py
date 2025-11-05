"""
Service layer for Bank Statement Entry Splits
Business logic and database operations
"""
from datetime import datetime
from math import ceil
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.db.models import BankStatementEntry, BankStatementEntrySplit, Category
from app.core.exceptions import BadRequestException, NotFoundException

from .schemas import (
    EntrySplitCreateRequest,
    EntrySplitListResponse,
    EntrySplitResponse,
    EntrySplitUpdateRequest,
)


class EntrySplitService:
    """Service for managing bank statement entry splits"""

    @staticmethod
    def create_split(
        db: Session, data: EntrySplitCreateRequest
    ) -> EntrySplitResponse:
        """
        Create a new bank statement entry split

        Args:
            db: Database session
            data: Entry split creation data

        Returns:
            Created entry split

        Raises:
            NotFoundException: If bank statement entry or category doesn't exist
        """
        # Verify bank statement entry exists
        entry = (
            db.query(BankStatementEntry)
            .filter(BankStatementEntry.id == data.bank_statement_entry_id)
            .first()
        )
        if not entry:
            raise NotFoundException(
                message=f"Bank statement entry with ID {data.bank_statement_entry_id} not found",
                details={"bank_statement_entry_id": str(data.bank_statement_entry_id)},
            )

        # Verify category exists
        category = db.query(Category).filter(Category.id == data.category_id).first()
        if not category:
            raise NotFoundException(
                message=f"Category with ID {data.category_id} not found",
                details={"category_id": str(data.category_id)},
            )

        # Create split
        split = BankStatementEntrySplit(
            bank_statement_entry_id=data.bank_statement_entry_id,
            category_id=data.category_id,
            amount=data.amount,
            description=data.description,
            modified_by=data.modified_by,
        )

        db.add(split)
        db.commit()
        db.refresh(split)

        return EntrySplitResponse.model_validate(split)

    @staticmethod
    def get_split(db: Session, split_id: UUID) -> EntrySplitResponse:
        """
        Get a bank statement entry split by ID

        Args:
            db: Database session
            split_id: Entry split ID

        Returns:
            Entry split details

        Raises:
            NotFoundException: If split not found
        """
        split = (
            db.query(BankStatementEntrySplit)
            .filter(BankStatementEntrySplit.id == split_id)
            .first()
        )

        if not split:
            raise NotFoundException(
                message=f"Bank statement entry split with ID {split_id} not found",
                details={"split_id": str(split_id)},
            )

        return EntrySplitResponse.model_validate(split)

    @staticmethod
    def get_splits(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        bank_statement_entry_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
    ) -> EntrySplitListResponse:
        """
        Get paginated list of bank statement entry splits with optional filtering

        Args:
            db: Database session
            page: Page number (1-indexed)
            page_size: Number of items per page (max 100)
            bank_statement_entry_id: Filter by bank statement entry ID
            category_id: Filter by category ID

        Returns:
            Paginated list of entry splits

        Raises:
            BadRequestException: If pagination parameters are invalid
        """
        # Validate pagination parameters
        if page < 1:
            raise BadRequestException(
                message="Page number must be greater than 0",
                details={"page": page},
            )

        if page_size > 100:
            raise BadRequestException(
                message="Page size cannot exceed 100",
                details={"page_size": page_size},
            )

        # Build query
        query = db.query(BankStatementEntrySplit)

        # Apply filters
        if bank_statement_entry_id:
            query = query.filter(
                BankStatementEntrySplit.bank_statement_entry_id
                == bank_statement_entry_id
            )

        if category_id:
            query = query.filter(BankStatementEntrySplit.category_id == category_id)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        splits = (
            query.order_by(BankStatementEntrySplit.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        # Calculate total pages
        total_pages = ceil(total / page_size) if page_size > 0 else 0

        return EntrySplitListResponse(
            items=[EntrySplitResponse.model_validate(s) for s in splits],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    def update_split(
        db: Session,
        split_id: UUID,
        data: EntrySplitUpdateRequest,
    ) -> EntrySplitResponse:
        """
        Update a bank statement entry split

        Args:
            db: Database session
            split_id: Entry split ID
            data: Update data

        Returns:
            Updated entry split

        Raises:
            NotFoundException: If split or category not found
        """
        split = (
            db.query(BankStatementEntrySplit)
            .filter(BankStatementEntrySplit.id == split_id)
            .first()
        )

        if not split:
            raise NotFoundException(
                message=f"Bank statement entry split with ID {split_id} not found",
                details={"split_id": str(split_id)},
            )

        # Verify category exists if provided
        if data.category_id:
            category = (
                db.query(Category).filter(Category.id == data.category_id).first()
            )
            if not category:
                raise NotFoundException(
                    message=f"Category with ID {data.category_id} not found",
                    details={"category_id": str(data.category_id)},
                )

        # Update fields if provided
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(split, field, value)

        # Update timestamp
        split.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(split)

        return EntrySplitResponse.model_validate(split)

    @staticmethod
    def delete_split(db: Session, split_id: UUID) -> None:
        """
        Delete a bank statement entry split (hard delete)

        Args:
            db: Database session
            split_id: Entry split ID

        Raises:
            NotFoundException: If split not found
        """
        split = (
            db.query(BankStatementEntrySplit)
            .filter(BankStatementEntrySplit.id == split_id)
            .first()
        )

        if not split:
            raise NotFoundException(
                message=f"Bank statement entry split with ID {split_id} not found",
                details={"split_id": str(split_id)},
            )

        db.delete(split)
        db.commit()
