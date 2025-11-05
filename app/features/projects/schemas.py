"""
Projects Pydantic schemas
Request and response models for API validation
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Request Schemas

class ProjectCreateRequest(BaseModel):
    """Schema for creating a new project"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    developer_name: str = Field(..., min_length=1, max_length=255, description="Developer name")
    investor_name: str = Field(..., min_length=1, max_length=255, description="Investor name")
    remarks: Optional[str] = Field(None, description="Additional remarks or notes")
    created_by: str = Field(..., min_length=1, max_length=255, description="User who created the project")

    @field_validator('name', 'developer_name', 'investor_name', 'created_by')
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Ensure strings are not just whitespace"""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sunset Apartments Phase 1",
                "developer_name": "ABC Development Corp",
                "investor_name": "XYZ Investment Group",
                "remarks": "High-rise residential project in downtown",
                "created_by": "john.doe@example.com"
            }
        }


class ProjectUpdateRequest(BaseModel):
    """Schema for updating an existing project (partial updates allowed)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    developer_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Developer name")
    investor_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Investor name")
    is_activated: Optional[bool] = Field(None, description="Whether the project is active")
    remarks: Optional[str] = Field(None, description="Additional remarks or notes")
    updated_by: Optional[str] = Field(None, min_length=1, max_length=255, description="User who updated the project")

    @field_validator('name', 'developer_name', 'investor_name', 'updated_by')
    @classmethod
    def validate_non_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure strings are not just whitespace if provided"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip() if v else None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sunset Apartments Phase 1 - Updated",
                "is_activated": True,
                "remarks": "Updated project scope",
                "updated_by": "jane.smith@example.com"
            }
        }


# Response Schemas

class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: UUID
    name: str
    developer_name: str
    investor_name: str
    is_activated: bool
    remarks: Optional[str]
    created_by: str
    created_at: datetime
    updated_by: Optional[str]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True  # Allows SQLAlchemy models to be converted to Pydantic
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Sunset Apartments Phase 1",
                "developer_name": "ABC Development Corp",
                "investor_name": "XYZ Investment Group",
                "is_activated": True,
                "remarks": "High-rise residential project in downtown",
                "created_by": "john.doe@example.com",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_by": "jane.smith@example.com",
                "updated_at": "2024-01-20T14:45:00Z"
            }
        }


class ProjectListResponse(BaseModel):
    """Schema for paginated project list response"""
    items: List[ProjectResponse]
    total: int = Field(..., description="Total number of projects")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Sunset Apartments Phase 1",
                        "developer_name": "ABC Development Corp",
                        "investor_name": "XYZ Investment Group",
                        "is_activated": True,
                        "remarks": "High-rise residential project",
                        "created_by": "john.doe@example.com",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_by": None,
                        "updated_at": None
                    }
                ],
                "total": 50,
                "page": 1,
                "page_size": 10,
                "total_pages": 5
            }
        }
