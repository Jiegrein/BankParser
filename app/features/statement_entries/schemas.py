"""
Pydantic schemas for Bank Statement Entries
"""
from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.core.db.models import TransactionType


class BankStatementEntryCreateRequest(BaseModel):
    """Request schema for creating a bank statement entry"""

    bank_statement_file_id: UUID = Field(..., description="Bank statement file ID")
    bank_account_id: UUID = Field(..., description="Bank account ID")
    category_id: Optional[UUID] = Field(None, description="Category ID for categorization")
    tags_csv: Optional[List[str]] = Field(None, description="Free-form tags")
    date: date = Field(..., description="Transaction date")
    time: Optional[time] = Field(None, description="Transaction time")
    description: str = Field(..., min_length=1, description="Transaction description")
    transaction_reference: Optional[str] = Field(None, description="Transaction reference number")
    debit_credit: TransactionType = Field(..., description="Transaction type (debit/credit)")
    amount: Decimal = Field(..., description="Transaction amount")
    balance: Optional[Decimal] = Field(None, description="Account balance after transaction")
    notes: Optional[str] = Field(None, description="Additional notes")
    modified_by: Optional[str] = Field(None, description="User who last modified this entry")

    @field_validator("description")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Strip leading/trailing whitespace"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Field cannot be empty or whitespace only")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate amount is positive"""
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class BankStatementEntryUpdateRequest(BaseModel):
    """Request schema for updating a bank statement entry"""

    category_id: Optional[UUID] = Field(None, description="Category ID for categorization")
    tags_csv: Optional[List[str]] = Field(None, description="Free-form tags")
    description: Optional[str] = Field(None, min_length=1, description="Transaction description")
    transaction_reference: Optional[str] = Field(None, description="Transaction reference number")
    debit_credit: Optional[TransactionType] = Field(None, description="Transaction type (debit/credit)")
    amount: Optional[Decimal] = Field(None, description="Transaction amount")
    balance: Optional[Decimal] = Field(None, description="Account balance after transaction")
    notes: Optional[str] = Field(None, description="Additional notes")
    updated_by: Optional[str] = Field(None, description="User who updated this entry")

    @field_validator("description")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Strip leading/trailing whitespace"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Field cannot be empty or whitespace only")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate amount is positive"""
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class BankStatementEntryResponse(BaseModel):
    """Response schema for a bank statement entry"""

    id: UUID
    bank_statement_file_id: UUID
    bank_account_id: UUID
    category_id: Optional[UUID]
    tags_csv: Optional[List[str]]
    date: date
    time: Optional[time]
    description: str
    transaction_reference: Optional[str]
    debit_credit: TransactionType
    amount: Decimal
    balance: Optional[Decimal]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    modified_by: Optional[str]
    updated_by: Optional[str]

    model_config = {"from_attributes": True}


class BankStatementEntryListResponse(BaseModel):
    """Response schema for paginated bank statement entries list"""

    items: List[BankStatementEntryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
