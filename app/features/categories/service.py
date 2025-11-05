"""
Categories Service
Business logic for category operations
"""
import math
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.db.models import Category
from app.core.exceptions import BadRequestException, NotFoundException

from .schemas import (
    CategoryCreateRequest,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdateRequest,
)


class CategoryService:
    """Service class for category business logic"""

    @staticmethod
    def create_category(db: Session, data: CategoryCreateRequest) -> CategoryResponse:
        """
        Create a new category

        Args:
            db: Database session
            data: Category creation data

        Returns:
            CategoryResponse: Created category
        """
        # Create new category
        category = Category(
            name=data.name,
            identification_regex=data.identification_regex,
            color=data.color,
            description=data.description,
            is_active=True,  # Default to active
            created_by=data.created_by,
        )

        db.add(category)
        db.commit()
        db.refresh(category)

        return CategoryResponse.model_validate(category)

    @staticmethod
    def get_category(db: Session, category_id: UUID) -> CategoryResponse:
        """
        Get a category by ID

        Args:
            db: Database session
            category_id: Category UUID

        Returns:
            CategoryResponse: Category details

        Raises:
            NotFoundException: If category not found
        """
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            raise NotFoundException(
                message=f"Category with ID {category_id} not found",
                details={"category_id": str(category_id)},
            )

        return CategoryResponse.model_validate(category)

    @staticmethod
    def get_categories(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> CategoryListResponse:
        """
        Get paginated list of categories with optional filters

        Args:
            db: Database session
            page: Page number (1-indexed)
            page_size: Number of items per page
            is_active: Filter by active status (optional)
            search: Search in name or description (optional)

        Returns:
            CategoryListResponse: Paginated list of categories

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
        query = db.query(Category)

        # Apply filters
        if is_active is not None:
            query = query.filter(Category.is_active == is_active)

        if search:
            search_filter = or_(
                Category.name.ilike(f"%{search}%"),
                Category.description.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        # Get total count
        total = query.count()

        # Calculate pagination
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        offset = (page - 1) * page_size

        # Order by created_at descending (newest first)
        query = query.order_by(Category.created_at.desc())

        # Apply pagination
        categories = query.offset(offset).limit(page_size).all()

        # Convert to response models
        items = [CategoryResponse.model_validate(category) for category in categories]

        return CategoryListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    def update_category(
        db: Session, category_id: UUID, data: CategoryUpdateRequest
    ) -> CategoryResponse:
        """
        Update an existing category

        Args:
            db: Database session
            category_id: Category UUID
            data: Update data (only provided fields will be updated)

        Returns:
            CategoryResponse: Updated category

        Raises:
            NotFoundException: If category not found
        """
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            raise NotFoundException(
                message=f"Category with ID {category_id} not found",
                details={"category_id": str(category_id)},
            )

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(category, field, value)

        # Update timestamp
        category.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(category)

        return CategoryResponse.model_validate(category)

    @staticmethod
    def delete_category(db: Session, category_id: UUID) -> None:
        """
        Delete a category (soft delete by setting is_active=False)

        Args:
            db: Database session
            category_id: Category UUID

        Raises:
            NotFoundException: If category not found
        """
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            raise NotFoundException(
                message=f"Category with ID {category_id} not found",
                details={"category_id": str(category_id)},
            )

        # Soft delete - set is_active to False
        category.is_active = False
        category.updated_at = datetime.utcnow()

        db.commit()
