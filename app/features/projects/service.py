"""
Projects service layer
Business logic and database operations
"""

import math
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.db.models import Project
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)

from .schemas import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)


class ProjectService:
    """Service class for project-related operations"""

    @staticmethod
    def create_project(db: Session, data: ProjectCreateRequest) -> ProjectResponse:
        """
        Create a new project

        Args:
            db: Database session
            data: Project creation data

        Returns:
            Created project

        Raises:
            ConflictException: If project with same name already exists (database will raise IntegrityError)
            BadRequestException: If validation fails
        """
        # Create new project instance
        project = Project(
            name=data.name,
            developer_name=data.developer_name,
            investor_name=data.investor_name,
            remarks=data.remarks,
            created_by=data.created_by,
            is_activated=True,  # New projects are active by default
        )

        # Add to session and commit
        db.add(project)
        db.commit()
        db.refresh(project)

        return ProjectResponse.model_validate(project)

    @staticmethod
    def get_project(db: Session, project_id: UUID) -> ProjectResponse:
        """
        Get a single project by ID

        Args:
            db: Database session
            project_id: Project UUID

        Returns:
            Project data

        Raises:
            NotFoundException: If project not found
        """
        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            raise NotFoundException(
                message=f"Project with ID {project_id} not found",
                details={"project_id": str(project_id)},
            )

        return ProjectResponse.model_validate(project)

    @staticmethod
    def get_projects(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        is_activated: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> ProjectListResponse:
        """
        Get paginated list of projects with optional filters

        Args:
            db: Database session
            page: Page number (1-indexed)
            page_size: Number of items per page (max 100)
            is_activated: Filter by activation status (None = all)
            search: Search in name, developer_name, or investor_name

        Returns:
            Paginated project list

        Raises:
            BadRequestException: If page or page_size is invalid
        """
        # Validate pagination parameters
        if page < 1:
            raise BadRequestException(
                message="Page number must be >= 1", details={"page": page}
            )

        if page_size < 1 or page_size > 100:
            raise BadRequestException(
                message="Page size must be between 1 and 100",
                details={"page_size": page_size},
            )

        # Build base query
        query = db.query(Project)

        # Apply filters
        if is_activated is not None:
            query = query.filter(Project.is_activated == is_activated)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Project.name.ilike(search_pattern))
                | (Project.developer_name.ilike(search_pattern))
                | (Project.investor_name.ilike(search_pattern))
            )

        # Get total count
        total = query.count()

        # Calculate total pages
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        # Apply pagination
        offset = (page - 1) * page_size
        projects = (
            query.order_by(Project.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        # Convert to response models
        items = [ProjectResponse.model_validate(project) for project in projects]

        return ProjectListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    def update_project(
        db: Session, project_id: UUID, data: ProjectUpdateRequest
    ) -> ProjectResponse:
        """
        Update an existing project (partial update)

        Args:
            db: Database session
            project_id: Project UUID
            data: Project update data (only provided fields will be updated)

        Returns:
            Updated project

        Raises:
            NotFoundException: If project not found
        """
        # Get existing project
        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            raise NotFoundException(
                message=f"Project with ID {project_id} not found",
                details={"project_id": str(project_id)},
            )

        # Update only provided fields (partial update)
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(project, field, value)

        # Update timestamp
        project.updated_at = datetime.utcnow()

        # Commit changes
        db.commit()
        db.refresh(project)

        return ProjectResponse.model_validate(project)

    @staticmethod
    def delete_project(db: Session, project_id: UUID) -> None:
        """
        Soft delete a project (set is_activated=False)

        Args:
            db: Database session
            project_id: Project UUID

        Raises:
            NotFoundException: If project not found
        """
        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            raise NotFoundException(
                message=f"Project with ID {project_id} not found",
                details={"project_id": str(project_id)},
            )

        # Soft delete - set is_activated to False
        project.is_activated = False
        project.updated_at = datetime.utcnow()

        db.commit()
