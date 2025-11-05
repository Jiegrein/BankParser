"""
Service layer for Bank Statement Files
Business logic and database operations
"""
from datetime import datetime
from math import ceil
from typing import Optional
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.db.models import BankAccount, BankStatementFile
from app.core.exceptions import BadRequestException, NotFoundException

from .schemas import (
    BankStatementFileCreateRequest,
    BankStatementFileListResponse,
    BankStatementFileResponse,
    BankStatementFileUpdateRequest,
)


class BankStatementFileService:
    """Service for managing bank statement files"""

    @staticmethod
    def create_statement_file(
        db: Session, data: BankStatementFileCreateRequest
    ) -> BankStatementFileResponse:
        """
        Create a new bank statement file

        Args:
            db: Database session
            data: Bank statement file creation data

        Returns:
            Created bank statement file

        Raises:
            NotFoundException: If bank account doesn't exist
        """
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

        # Create statement file
        statement_file = BankStatementFile(
            bank_account_id=data.bank_account_id,
            file_path=data.file_path,
            period_start=data.period_start,
            period_end=data.period_end,
            uploaded_by=data.uploaded_by,
        )

        db.add(statement_file)
        db.commit()
        db.refresh(statement_file)

        return BankStatementFileResponse.model_validate(statement_file)

    @staticmethod
    def get_statement_file(db: Session, statement_file_id: UUID) -> BankStatementFileResponse:
        """
        Get a bank statement file by ID

        Args:
            db: Database session
            statement_file_id: Bank statement file ID

        Returns:
            Bank statement file details

        Raises:
            NotFoundException: If statement file not found
        """
        statement_file = (
            db.query(BankStatementFile)
            .filter(BankStatementFile.id == statement_file_id)
            .first()
        )

        if not statement_file:
            raise NotFoundException(
                message=f"Bank statement file with ID {statement_file_id} not found",
                details={"statement_file_id": str(statement_file_id)},
            )

        return BankStatementFileResponse.model_validate(statement_file)

    @staticmethod
    def get_statement_files(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        bank_account_id: Optional[UUID] = None,
        search: Optional[str] = None,
    ) -> BankStatementFileListResponse:
        """
        Get paginated list of bank statement files with optional filtering

        Args:
            db: Database session
            page: Page number (1-indexed)
            page_size: Number of items per page (max 100)
            bank_account_id: Filter by bank account ID
            search: Search in file_path

        Returns:
            Paginated list of bank statement files

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
        query = db.query(BankStatementFile)

        # Apply filters
        if bank_account_id:
            query = query.filter(BankStatementFile.bank_account_id == bank_account_id)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    BankStatementFile.file_path.ilike(search_filter),
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        statement_files = (
            query.order_by(BankStatementFile.uploaded_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        # Calculate total pages
        total_pages = ceil(total / page_size) if page_size > 0 else 0

        return BankStatementFileListResponse(
            items=[BankStatementFileResponse.model_validate(sf) for sf in statement_files],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    def update_statement_file(
        db: Session,
        statement_file_id: UUID,
        data: BankStatementFileUpdateRequest,
    ) -> BankStatementFileResponse:
        """
        Update a bank statement file

        Args:
            db: Database session
            statement_file_id: Bank statement file ID
            data: Update data

        Returns:
            Updated bank statement file

        Raises:
            NotFoundException: If statement file not found
        """
        statement_file = (
            db.query(BankStatementFile)
            .filter(BankStatementFile.id == statement_file_id)
            .first()
        )

        if not statement_file:
            raise NotFoundException(
                message=f"Bank statement file with ID {statement_file_id} not found",
                details={"statement_file_id": str(statement_file_id)},
            )

        # Update fields if provided
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(statement_file, field, value)

        # Update timestamp
        statement_file.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(statement_file)

        return BankStatementFileResponse.model_validate(statement_file)

    @staticmethod
    def delete_statement_file(db: Session, statement_file_id: UUID) -> None:
        """
        Delete a bank statement file (hard delete)

        Args:
            db: Database session
            statement_file_id: Bank statement file ID

        Raises:
            NotFoundException: If statement file not found
        """
        statement_file = (
            db.query(BankStatementFile)
            .filter(BankStatementFile.id == statement_file_id)
            .first()
        )

        if not statement_file:
            raise NotFoundException(
                message=f"Bank statement file with ID {statement_file_id} not found",
                details={"statement_file_id": str(statement_file_id)},
            )

        db.delete(statement_file)
        db.commit()
