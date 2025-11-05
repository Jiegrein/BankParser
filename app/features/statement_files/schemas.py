"""
Pydantic schemas for Bank Statement Files
"""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class BankStatementFileCreateRequest(BaseModel):
    """Request schema for creating a bank statement file"""

    bank_account_id: UUID = Field(..., description="Bank account ID this statement belongs to")
    file_path: str = Field(..., min_length=1, description="Azure Blob Storage URL")
    period_start: date = Field(..., description="Statement period start date")
    period_end: date = Field(..., description="Statement period end date")
    uploaded_by: str = Field(..., min_length=1, description="User who uploaded this file")

    @field_validator("file_path", "uploaded_by")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Strip leading/trailing whitespace"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Field cannot be empty or whitespace only")
        return v

    @field_validator("period_end")
    @classmethod
    def validate_period(cls, v: date, info) -> date:
        """Validate period_end is after period_start"""
        if "period_start" in info.data and v < info.data["period_start"]:
            raise ValueError("period_end must be after period_start")
        return v


class BankStatementFileUpdateRequest(BaseModel):
    """Request schema for updating a bank statement file"""

    file_path: Optional[str] = Field(None, min_length=1, description="Azure Blob Storage URL")
    period_start: Optional[date] = Field(None, description="Statement period start date")
    period_end: Optional[date] = Field(None, description="Statement period end date")
    updated_by: Optional[str] = Field(None, min_length=1, description="User who updated this file")

    @field_validator("file_path", "updated_by")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Strip leading/trailing whitespace"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Field cannot be empty or whitespace only")
        return v


class BankStatementFileResponse(BaseModel):
    """Response schema for a bank statement file"""

    id: UUID
    bank_account_id: UUID
    file_path: str
    period_start: date
    period_end: date
    uploaded_by: str
    uploaded_at: datetime
    updated_at: Optional[datetime]
    updated_by: Optional[str]

    model_config = {"from_attributes": True}


class BankStatementFileListResponse(BaseModel):
    """Response schema for paginated bank statement files list"""

    items: List[BankStatementFileResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
