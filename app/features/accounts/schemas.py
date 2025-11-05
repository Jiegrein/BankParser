"""
Bank Accounts Pydantic schemas
Request and response models for API validation
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class BankAccountCreateRequest(BaseModel):
    """Request schema for creating a bank account"""
    project_id: UUID = Field(..., description="Project UUID this account belongs to")
    account_number: str = Field(..., min_length=1, description="Account number (last 4 digits only)")
    bank_name: str = Field(..., min_length=1, description="Bank name")
    account_type: str = Field(..., min_length=1, description="Account type (e.g., checking, savings)")
    color: Optional[str] = Field(None, description="Color code for visual display")
    position_x: Optional[Decimal] = Field(None, description="X coordinate for visual positioning")
    position_y: Optional[Decimal] = Field(None, description="Y coordinate for visual positioning")
    created_by: str = Field(..., min_length=1, description="User who created this account")

    @field_validator("account_number", "bank_name", "account_type", "created_by")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Strip leading/trailing whitespace"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Field cannot be empty or whitespace only")
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "account_number": "1234",
                "bank_name": "Chase Bank",
                "account_type": "checking",
                "color": "#FF5733",
                "position_x": 100.5,
                "position_y": 200.3,
                "created_by": "user@example.com"
            }
        }


class BankAccountUpdateRequest(BaseModel):
    """Request schema for updating a bank account (all fields optional)"""
    account_number: Optional[str] = Field(None, min_length=1, description="Account number (last 4 digits only)")
    bank_name: Optional[str] = Field(None, min_length=1, description="Bank name")
    account_type: Optional[str] = Field(None, min_length=1, description="Account type")
    color: Optional[str] = Field(None, description="Color code for visual display")
    position_x: Optional[Decimal] = Field(None, description="X coordinate for visual positioning")
    position_y: Optional[Decimal] = Field(None, description="Y coordinate for visual positioning")
    updated_by: Optional[str] = Field(None, min_length=1, description="User who updated this account")

    @field_validator("account_number", "bank_name", "account_type", "updated_by")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Strip leading/trailing whitespace if provided"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Field cannot be empty or whitespace only")
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "bank_name": "Updated Bank Name",
                "color": "#00FF00",
                "updated_by": "admin@example.com"
            }
        }


class BankAccountResponse(BaseModel):
    """Response schema for bank account"""
    id: UUID
    project_id: UUID
    account_number: str
    bank_name: str
    account_type: str
    color: Optional[str]
    position_x: Optional[Decimal]
    position_y: Optional[Decimal]
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]
    updated_by: Optional[str]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "account_number": "1234",
                "bank_name": "Chase Bank",
                "account_type": "checking",
                "color": "#FF5733",
                "position_x": 100.5,
                "position_y": 200.3,
                "created_by": "user@example.com",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": None,
                "updated_by": None
            }
        }


class BankAccountListResponse(BaseModel):
    """Response schema for paginated list of bank accounts"""
    items: list[BankAccountResponse]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 10,
                "page": 1,
                "page_size": 10,
                "total_pages": 1
            }
        }
