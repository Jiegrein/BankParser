"""
Bank Accounts Service
Business logic for bank account operations
"""

import math
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.db.models import BankAccount, Project
from app.core.exceptions import BadRequestException, NotFoundException

from .schemas import (
    BankAccountCreateRequest,
    BankAccountListResponse,
    BankAccountResponse,
    BankAccountUpdateRequest,
)


class BankAccountService:
    """Service class for bank account business logic"""

    @staticmethod
    def create_bank_account(
        db: Session, data: BankAccountCreateRequest
    ) -> BankAccountResponse:
        """
        Create a new bank account

        Args:
            db: Database session
            data: Bank account creation data

        Returns:
            BankAccountResponse: Created bank account

        Raises:
            NotFoundException: If project not found
        """
        # Verify project exists
        project = db.query(Project).filter(Project.id == data.project_id).first()
        if not project:
            raise NotFoundException(
                message=f"Project with ID {data.project_id} not found",
                details={"project_id": str(data.project_id)},
            )

        # Create new bank account
        bank_account = BankAccount(
            project_id=data.project_id,
            account_number=data.account_number,
            bank_name=data.bank_name,
            account_type=data.account_type,
            color=data.color,
            position_x=data.position_x,
            position_y=data.position_y,
            created_by=data.created_by,
        )

        db.add(bank_account)
        db.commit()
        db.refresh(bank_account)

        return BankAccountResponse.model_validate(bank_account)

    @staticmethod
    def get_bank_account(db: Session, account_id: UUID) -> BankAccountResponse:
        """
        Get a bank account by ID

        Args:
            db: Database session
            account_id: Bank account UUID

        Returns:
            BankAccountResponse: Bank account details

        Raises:
            NotFoundException: If bank account not found
        """
        bank_account = (
            db.query(BankAccount).filter(BankAccount.id == account_id).first()
        )

        if not bank_account:
            raise NotFoundException(
                message=f"Bank account with ID {account_id} not found",
                details={"account_id": str(account_id)},
            )

        return BankAccountResponse.model_validate(bank_account)

    @staticmethod
    def get_bank_accounts(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        project_id: Optional[UUID] = None,
        search: Optional[str] = None,
    ) -> BankAccountListResponse:
        """
        Get paginated list of bank accounts with optional filters

        Args:
            db: Database session
            page: Page number (1-indexed)
            page_size: Number of items per page
            project_id: Filter by project ID (optional)
            search: Search in bank_name, account_number, or account_type (optional)

        Returns:
            BankAccountListResponse: Paginated list of bank accounts

        Raises:
            BadRequestException: If pagination parameters are invalid
        """
        # Validate pagination parameters
        if page < 1:
            raise BadRequestException(
                message="Page number must be greater than 0", details={"page": page}
            )

        if page_size < 1 or page_size > 100:
            raise BadRequestException(
                message="Page size must be between 1 and 100",
                details={"page_size": page_size},
            )

        # Build query
        query = db.query(BankAccount)

        # Apply filters
        if project_id is not None:
            query = query.filter(BankAccount.project_id == project_id)

        if search:
            search_filter = or_(
                BankAccount.bank_name.ilike(f"%{search}%"),
                BankAccount.account_number.ilike(f"%{search}%"),
                BankAccount.account_type.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        # Get total count
        total = query.count()

        # Calculate pagination
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        offset = (page - 1) * page_size

        # Order by created_at descending (newest first)
        query = query.order_by(BankAccount.created_at.desc())

        # Apply pagination
        bank_accounts = query.offset(offset).limit(page_size).all()

        # Convert to response models
        items = [
            BankAccountResponse.model_validate(account) for account in bank_accounts
        ]

        return BankAccountListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    def update_bank_account(
        db: Session, account_id: UUID, data: BankAccountUpdateRequest
    ) -> BankAccountResponse:
        """
        Update an existing bank account

        Args:
            db: Database session
            account_id: Bank account UUID
            data: Update data (only provided fields will be updated)

        Returns:
            BankAccountResponse: Updated bank account

        Raises:
            NotFoundException: If bank account not found
        """
        bank_account = (
            db.query(BankAccount).filter(BankAccount.id == account_id).first()
        )

        if not bank_account:
            raise NotFoundException(
                message=f"Bank account with ID {account_id} not found",
                details={"account_id": str(account_id)},
            )

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(bank_account, field, value)

        # Update timestamp
        bank_account.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(bank_account)

        return BankAccountResponse.model_validate(bank_account)

    @staticmethod
    def delete_bank_account(db: Session, account_id: UUID) -> None:
        """
        Delete a bank account (hard delete)

        Note: Since BankAccount model doesn't have is_activated field,
        this performs a hard delete. Consider adding is_activated for soft delete.

        Args:
            db: Database session
            account_id: Bank account UUID

        Raises:
            NotFoundException: If bank account not found
        """
        bank_account = (
            db.query(BankAccount).filter(BankAccount.id == account_id).first()
        )

        if not bank_account:
            raise NotFoundException(
                message=f"Bank account with ID {account_id} not found",
                details={"account_id": str(account_id)},
            )

        # Hard delete
        db.delete(bank_account)
        db.commit()
