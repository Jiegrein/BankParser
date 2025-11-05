"""
Service layer for Bank Statement Entries
Business logic and database operations
"""
from datetime import datetime
from math import ceil
from typing import Optional
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.db.models import (
    BankAccount,
    BankStatementEntry,
    BankStatementFile,
    Category,
    TransactionType,
)
from app.core.exceptions import BadRequestException, NotFoundException

from .schemas import (
    BankStatementEntryCreateRequest,
    BankStatementEntryListResponse,
    BankStatementEntryResponse,
    BankStatementEntryUpdateRequest,
)


class BankStatementEntryService:
    """Service for managing bank statement entries"""

    @staticmethod
    def create_entry(
        db: Session, data: BankStatementEntryCreateRequest
    ) -> BankStatementEntryResponse:
        """
        Create a new bank statement entry

        Args:
            db: Database session
            data: Bank statement entry creation data

        Returns:
            Created bank statement entry

        Raises:
            NotFoundException: If bank statement file, bank account, or category doesn't exist
        """
        # Verify bank statement file exists
        statement_file = (
            db.query(BankStatementFile)
            .filter(BankStatementFile.id == data.bank_statement_file_id)
            .first()
        )
        if not statement_file:
            raise NotFoundException(
                message=f"Bank statement file with ID {data.bank_statement_file_id} not found",
                details={"bank_statement_file_id": str(data.bank_statement_file_id)},
            )

        # Verify bank account exists
        bank_account = (
            db.query(BankAccount)
            .filter(BankAccount.id == data.bank_account_id)
            .first()
        )
        if not bank_account:
            raise NotFoundException(
                message=f"Bank account with ID {data.bank_account_id} not found",
                details={"bank_account_id": str(data.bank_account_id)},
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

        # Create entry
        entry = BankStatementEntry(
            bank_statement_file_id=data.bank_statement_file_id,
            bank_account_id=data.bank_account_id,
            category_id=data.category_id,
            tags_csv=data.tags_csv,  # Will be stored as JSONB in PostgreSQL
            date=data.date,
            time=data.time,
            description=data.description,
            transaction_reference=data.transaction_reference,
            debit_credit=data.debit_credit,
            amount=data.amount,
            balance=data.balance,
            notes=data.notes,
            modified_by=data.modified_by,
        )

        db.add(entry)
        db.commit()
        db.refresh(entry)

        return BankStatementEntryResponse.model_validate(entry)

    @staticmethod
    def get_entry(db: Session, entry_id: UUID) -> BankStatementEntryResponse:
        """
        Get a bank statement entry by ID

        Args:
            db: Database session
            entry_id: Bank statement entry ID

        Returns:
            Bank statement entry details

        Raises:
            NotFoundException: If entry not found
        """
        entry = (
            db.query(BankStatementEntry)
            .filter(BankStatementEntry.id == entry_id)
            .first()
        )

        if not entry:
            raise NotFoundException(
                message=f"Bank statement entry with ID {entry_id} not found",
                details={"entry_id": str(entry_id)},
            )

        return BankStatementEntryResponse.model_validate(entry)

    @staticmethod
    def get_entries(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        bank_account_id: Optional[UUID] = None,
        bank_statement_file_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        transaction_type: Optional[TransactionType] = None,
        search: Optional[str] = None,
    ) -> BankStatementEntryListResponse:
        """
        Get paginated list of bank statement entries with optional filtering

        Args:
            db: Database session
            page: Page number (1-indexed)
            page_size: Number of items per page (max 100)
            bank_account_id: Filter by bank account ID
            bank_statement_file_id: Filter by statement file ID
            category_id: Filter by category ID
            transaction_type: Filter by transaction type (debit/credit)
            search: Search in description

        Returns:
            Paginated list of bank statement entries

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
        query = db.query(BankStatementEntry)

        # Apply filters
        if bank_account_id:
            query = query.filter(BankStatementEntry.bank_account_id == bank_account_id)

        if bank_statement_file_id:
            query = query.filter(
                BankStatementEntry.bank_statement_file_id == bank_statement_file_id
            )

        if category_id:
            query = query.filter(BankStatementEntry.category_id == category_id)

        if transaction_type:
            query = query.filter(BankStatementEntry.debit_credit == transaction_type)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    BankStatementEntry.description.ilike(search_filter),
                    BankStatementEntry.transaction_reference.ilike(search_filter),
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        entries = (
            query.order_by(BankStatementEntry.date.desc(), BankStatementEntry.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        # Calculate total pages
        total_pages = ceil(total / page_size) if page_size > 0 else 0

        return BankStatementEntryListResponse(
            items=[BankStatementEntryResponse.model_validate(e) for e in entries],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    def update_entry(
        db: Session,
        entry_id: UUID,
        data: BankStatementEntryUpdateRequest,
    ) -> BankStatementEntryResponse:
        """
        Update a bank statement entry

        Args:
            db: Database session
            entry_id: Bank statement entry ID
            data: Update data

        Returns:
            Updated bank statement entry

        Raises:
            NotFoundException: If entry or category not found
        """
        entry = (
            db.query(BankStatementEntry)
            .filter(BankStatementEntry.id == entry_id)
            .first()
        )

        if not entry:
            raise NotFoundException(
                message=f"Bank statement entry with ID {entry_id} not found",
                details={"entry_id": str(entry_id)},
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
            setattr(entry, field, value)

        # Update timestamp
        entry.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(entry)

        return BankStatementEntryResponse.model_validate(entry)

    @staticmethod
    def delete_entry(db: Session, entry_id: UUID) -> None:
        """
        Delete a bank statement entry (hard delete)

        Args:
            db: Database session
            entry_id: Bank statement entry ID

        Raises:
            NotFoundException: If entry not found
        """
        entry = (
            db.query(BankStatementEntry)
            .filter(BankStatementEntry.id == entry_id)
            .first()
        )

        if not entry:
            raise NotFoundException(
                message=f"Bank statement entry with ID {entry_id} not found",
                details={"entry_id": str(entry_id)},
            )

        db.delete(entry)
        db.commit()
