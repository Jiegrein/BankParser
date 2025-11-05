"""
Projects API routes
REST endpoints for project management
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from .schemas import ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse, ProjectListResponse
from .service import ProjectService

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/v1/projects",
    tags=["Projects"]
)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Create a new project with the provided details"
)
async def create_project(
    data: ProjectCreateRequest,
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Create a new project

    - **name**: Project name (required)
    - **developer_name**: Developer name (required)
    - **investor_name**: Investor name (required)
    - **remarks**: Additional remarks (optional)
    - **created_by**: User who created the project (required)
    """
    return ProjectService.create_project(db, data)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get a project by ID",
    description="Retrieve a single project by its UUID"
)
async def get_project(
    project_id: UUID,
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Get a single project by ID

    - **project_id**: UUID of the project
    """
    return ProjectService.get_project(db, project_id)


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="Get list of projects",
    description="Retrieve a paginated list of projects with optional filters"
)
async def get_projects(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    is_activated: Optional[bool] = Query(None, description="Filter by activation status (true/false/null for all)"),
    search: Optional[str] = Query(None, description="Search in name, developer, or investor"),
    db: Session = Depends(get_db)
) -> ProjectListResponse:
    """
    Get paginated list of projects

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **is_activated**: Filter by active/inactive status (optional)
    - **search**: Search text for name, developer_name, or investor_name (optional)
    """
    return ProjectService.get_projects(
        db=db,
        page=page,
        page_size=page_size,
        is_activated=is_activated,
        search=search
    )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project",
    description="Update an existing project (partial updates allowed)"
)
async def update_project(
    project_id: UUID,
    data: ProjectUpdateRequest,
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Update an existing project

    Only provided fields will be updated (partial update).

    - **project_id**: UUID of the project to update
    - **name**: New project name (optional)
    - **developer_name**: New developer name (optional)
    - **investor_name**: New investor name (optional)
    - **is_activated**: Active status (optional)
    - **remarks**: Updated remarks (optional)
    - **updated_by**: User who updated the project (optional)
    """
    return ProjectService.update_project(db, project_id, data)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project (soft delete)",
    description="Soft delete a project by setting is_activated to false"
)
async def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """
    Soft delete a project

    Sets is_activated to false. The project will still exist in the database
    but will be marked as inactive.

    - **project_id**: UUID of the project to delete
    """
    ProjectService.delete_project(db, project_id)
