"""
Categories API routes
REST endpoints for category management
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db

from .schemas import (
    CategoryCreateRequest,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdateRequest,
)
from .service import CategoryService

# Create router with prefix and tags
router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
    description="Create a new category for transaction categorization",
)
async def create_category(
    data: CategoryCreateRequest, db: Session = Depends(get_db)
) -> CategoryResponse:
    """
    Create a new category

    - **name**: Category name (required)
    - **identification_regex**: Regex pattern for auto-categorization (optional)
    - **color**: Color code for visual display (optional)
    - **description**: Category description (optional)
    - **created_by**: User who created this category (required)
    """
    return CategoryService.create_category(db, data)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get a category by ID",
    description="Retrieve a single category by its UUID",
)
async def get_category(
    category_id: UUID, db: Session = Depends(get_db)
) -> CategoryResponse:
    """
    Get a single category by ID

    - **category_id**: UUID of the category
    """
    return CategoryService.get_category(db, category_id)


@router.get(
    "",
    response_model=CategoryListResponse,
    summary="Get list of categories",
    description="Retrieve a paginated list of categories with optional filters",
)
async def get_categories(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(
        10, ge=1, le=100, description="Number of items per page (max 100)"
    ),
    is_active: Optional[bool] = Query(
        None, description="Filter by active status (true/false/null for all)"
    ),
    search: Optional[str] = Query(
        None, description="Search in category name or description"
    ),
    db: Session = Depends(get_db),
) -> CategoryListResponse:
    """
    Get paginated list of categories

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **is_active**: Filter by active/inactive status (optional)
    - **search**: Search text for name or description (optional)
    """
    return CategoryService.get_categories(
        db=db, page=page, page_size=page_size, is_active=is_active, search=search
    )


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update a category",
    description="Update an existing category (partial updates allowed)",
)
async def update_category(
    category_id: UUID, data: CategoryUpdateRequest, db: Session = Depends(get_db)
) -> CategoryResponse:
    """
    Update an existing category

    Only provided fields will be updated (partial update).

    - **category_id**: UUID of the category to update
    - **name**: New category name (optional)
    - **identification_regex**: New regex pattern (optional)
    - **color**: New color code (optional)
    - **is_active**: Active status (optional)
    - **description**: New description (optional)
    - **updated_by**: User who updated this category (optional)
    """
    return CategoryService.update_category(db, category_id, data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category (soft delete)",
    description="Soft delete a category by setting is_active to false",
)
async def delete_category(category_id: UUID, db: Session = Depends(get_db)) -> None:
    """
    Soft delete a category

    Sets is_active to false. The category will still exist in the database
    but will be marked as inactive.

    - **category_id**: UUID of the category to delete
    """
    CategoryService.delete_category(db, category_id)
