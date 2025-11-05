"""
Categories Pydantic schemas
Request and response models for API validation
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class CategoryCreateRequest(BaseModel):
    """Request schema for creating a category"""
    name: str = Field(..., min_length=1, description="Category name")
    identification_regex: Optional[str] = Field(None, description="Regex pattern for auto-categorization")
    color: Optional[str] = Field(None, description="Color code for visual display")
    description: Optional[str] = Field(None, description="Category description")
    created_by: str = Field(..., min_length=1, description="User who created this category")

    @field_validator("name", "created_by")
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
                "name": "Payroll",
                "identification_regex": ".*SALARY.*|.*PAYROLL.*",
                "color": "#4CAF50",
                "description": "Employee salary and payroll transactions",
                "created_by": "admin@example.com"
            }
        }


class CategoryUpdateRequest(BaseModel):
    """Request schema for updating a category (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, description="Category name")
    identification_regex: Optional[str] = Field(None, description="Regex pattern for auto-categorization")
    color: Optional[str] = Field(None, description="Color code for visual display")
    is_active: Optional[bool] = Field(None, description="Active status")
    description: Optional[str] = Field(None, description="Category description")
    updated_by: Optional[str] = Field(None, min_length=1, description="User who updated this category")

    @field_validator("name", "updated_by")
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
                "name": "Updated Category Name",
                "color": "#FF5722",
                "is_active": True,
                "updated_by": "admin@example.com"
            }
        }


class CategoryResponse(BaseModel):
    """Response schema for category"""
    id: UUID
    name: str
    identification_regex: Optional[str]
    color: Optional[str]
    is_active: bool
    description: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]
    updated_by: Optional[str]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Payroll",
                "identification_regex": ".*SALARY.*|.*PAYROLL.*",
                "color": "#4CAF50",
                "is_active": True,
                "description": "Employee salary and payroll transactions",
                "created_by": "admin@example.com",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": None,
                "updated_by": None
            }
        }


class CategoryListResponse(BaseModel):
    """Response schema for paginated list of categories"""
    items: list[CategoryResponse]
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
