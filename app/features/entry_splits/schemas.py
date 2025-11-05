"""
Pydantic schemas for Bank Statement Entry Splits
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class EntrySplitCreateRequest(BaseModel):
    """Request schema for creating a bank statement entry split"""

    bank_statement_entry_id: UUID = Field(..., description="Bank statement entry ID")
    category_id: UUID = Field(..., description="Category ID for this split")
    amount: Decimal = Field(..., description="Split amount")
    description: Optional[str] = Field(None, description="Split description")
    modified_by: Optional[str] = Field(None, description="User who created this split")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate amount is positive"""
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @field_validator("description")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Strip leading/trailing whitespace"""
        if v is not None:
            v = v.strip()
            if not v:
                return None  # Convert empty string to None
        return v


class EntrySplitUpdateRequest(BaseModel):
    """Request schema for updating a bank statement entry split"""

    category_id: Optional[UUID] = Field(None, description="Category ID for this split")
    amount: Optional[Decimal] = Field(None, description="Split amount")
    description: Optional[str] = Field(None, description="Split description")
    updated_by: Optional[str] = Field(None, description="User who updated this split")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate amount is positive"""
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @field_validator("description")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Strip leading/trailing whitespace"""
        if v is not None:
            v = v.strip()
            if not v:
                return None  # Convert empty string to None
        return v


class EntrySplitResponse(BaseModel):
    """Response schema for a bank statement entry split"""

    id: UUID
    bank_statement_entry_id: UUID
    category_id: UUID
    amount: Decimal
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    modified_by: Optional[str]
    updated_by: Optional[str]

    model_config = {"from_attributes": True}


class EntrySplitListResponse(BaseModel):
    """Response schema for paginated bank statement entry splits list"""

    items: List[EntrySplitResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
