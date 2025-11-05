"""
Integration tests for Projects service (with real test database)
Tests database queries and transactions with SQLite
"""
import pytest
from uuid import uuid4

from app.features.projects.service import ProjectService
from app.features.projects.schemas import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectListResponse
)
from app.core.db.models import Project
from app.core.exceptions import NotFoundException, BadRequestException


class TestProjectServiceIntegration:
    """Integration tests for ProjectService with real test database"""

    def test_create_project_saves_to_database(self, test_db):
        """Test create_project persists data to database"""
        # Arrange
        data = ProjectCreateRequest(
            name="Integration Test Project",
            developer_name="Integration Dev",
            investor_name="Integration Investor",
            remarks="Integration test",
            created_by="integration@test.com"
        )

        # Act
        result = ProjectService.create_project(test_db, data)

        # Assert
        assert result.id is not None
        assert result.name == "Integration Test Project"
        assert result.is_activated is True

        # Verify in database
        db_project = test_db.query(Project).filter(Project.id == result.id).first()
        assert db_project is not None
        assert db_project.name == "Integration Test Project"
        assert db_project.developer_name == "Integration Dev"

    def test_create_project_generates_uuid(self, test_db):
        """Test create_project generates valid UUID"""
        # Arrange
        data = ProjectCreateRequest(
            name="UUID Test",
            developer_name="Dev",
            investor_name="Investor",
            created_by="test@test.com"
        )

        # Act
        result = ProjectService.create_project(test_db, data)

        # Assert
        assert result.id is not None
        assert isinstance(result.id, type(uuid4()))

    def test_create_project_sets_timestamps(self, test_db):
        """Test create_project sets created_at and updated_at"""
        # Arrange
        data = ProjectCreateRequest(
            name="Timestamp Test",
            developer_name="Dev",
            investor_name="Investor",
            created_by="test@test.com"
        )

        # Act
        result = ProjectService.create_project(test_db, data)

        # Assert
        assert result.created_at is not None
        assert result.updated_at is not None
        assert result.updated_by is None

    def test_get_project_retrieves_existing_project(self, test_db, sample_project):
        """Test get_project retrieves existing project from database"""
        # Act
        result = ProjectService.get_project(test_db, sample_project.id)

        # Assert
        assert result.id == sample_project.id
        assert result.name == sample_project.name
        assert result.developer_name == sample_project.developer_name

    def test_get_project_raises_not_found_for_missing_project(self, test_db):
        """Test get_project raises NotFoundException for non-existent project"""
        # Arrange
        random_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            ProjectService.get_project(test_db, random_id)

        assert str(random_id) in exc_info.value.details["project_id"]

    def test_get_projects_returns_paginated_list(self, test_db, multiple_projects):
        """Test get_projects returns paginated results"""
        # Act
        result = ProjectService.get_projects(test_db, page=1, page_size=10)

        # Assert
        assert isinstance(result, ProjectListResponse)
        assert result.total == 5
        assert len(result.items) == 5
        assert result.page == 1
        assert result.page_size == 10
        assert result.total_pages == 1

    def test_get_projects_pagination_works_correctly(self, test_db, multiple_projects):
        """Test get_projects pagination splits results correctly"""
        # Act - Page 1
        page1 = ProjectService.get_projects(test_db, page=1, page_size=2)
        # Act - Page 2
        page2 = ProjectService.get_projects(test_db, page=2, page_size=2)

        # Assert
        assert page1.total == 5
        assert len(page1.items) == 2
        assert page1.total_pages == 3

        assert page2.total == 5
        assert len(page2.items) == 2
        assert page2.total_pages == 3

        # Ensure different items
        page1_ids = {item.id for item in page1.items}
        page2_ids = {item.id for item in page2.items}
        assert page1_ids.isdisjoint(page2_ids)

    def test_get_projects_filters_by_is_activated(self, test_db, multiple_projects):
        """Test get_projects filters by is_activated status"""
        # Act - Get only active
        active_result = ProjectService.get_projects(
            test_db, page=1, page_size=10, is_activated=True
        )

        # Act - Get only inactive
        inactive_result = ProjectService.get_projects(
            test_db, page=1, page_size=10, is_activated=False
        )

        # Assert
        assert active_result.total == 3  # Projects 0, 2, 4 are active
        assert inactive_result.total == 2  # Projects 1, 3 are inactive

        for item in active_result.items:
            assert item.is_activated is True

        for item in inactive_result.items:
            assert item.is_activated is False

    def test_get_projects_search_by_name(self, test_db, multiple_projects):
        """Test get_projects searches by project name"""
        # Act
        result = ProjectService.get_projects(
            test_db, page=1, page_size=10, search="Project 3"
        )

        # Assert
        assert result.total == 1
        assert result.items[0].name == "Project 3"

    def test_get_projects_search_by_developer(self, test_db, multiple_projects):
        """Test get_projects searches by developer name"""
        # Act
        result = ProjectService.get_projects(
            test_db, page=1, page_size=10, search="Developer 2"
        )

        # Assert
        assert result.total == 1
        assert result.items[0].developer_name == "Developer 2"

    def test_get_projects_search_is_case_insensitive(self, test_db, multiple_projects):
        """Test get_projects search is case-insensitive"""
        # Act
        result = ProjectService.get_projects(
            test_db, page=1, page_size=10, search="project"
        )

        # Assert - Should find all projects (all have "Project" in name)
        assert result.total == 5

    def test_get_projects_orders_by_created_at_desc(self, test_db, multiple_projects):
        """Test get_projects returns newest projects first"""
        # Act
        result = ProjectService.get_projects(test_db, page=1, page_size=10)

        # Assert - Newest first
        for i in range(len(result.items) - 1):
            assert result.items[i].created_at >= result.items[i + 1].created_at

    def test_update_project_updates_database(self, test_db, sample_project):
        """Test update_project persists changes to database"""
        # Arrange
        data = ProjectUpdateRequest(
            name="Updated Project Name",
            remarks="Updated remarks",
            updated_by="updater@test.com"
        )

        # Act
        result = ProjectService.update_project(test_db, sample_project.id, data)

        # Assert
        assert result.name == "Updated Project Name"
        assert result.remarks == "Updated remarks"
        assert result.updated_by == "updater@test.com"
        assert result.updated_at > sample_project.created_at

        # Verify in database
        db_project = test_db.query(Project).filter(Project.id == sample_project.id).first()
        assert db_project.name == "Updated Project Name"

    def test_update_project_partial_update_preserves_other_fields(self, test_db, sample_project):
        """Test update_project only updates provided fields"""
        # Arrange
        original_developer = sample_project.developer_name
        data = ProjectUpdateRequest(name="New Name Only")

        # Act
        result = ProjectService.update_project(test_db, sample_project.id, data)

        # Assert
        assert result.name == "New Name Only"
        assert result.developer_name == original_developer  # Unchanged

    def test_update_project_raises_not_found_for_missing_project(self, test_db):
        """Test update_project raises NotFoundException"""
        # Arrange
        random_id = uuid4()
        data = ProjectUpdateRequest(name="Updated")

        # Act & Assert
        with pytest.raises(NotFoundException):
            ProjectService.update_project(test_db, random_id, data)

    def test_delete_project_soft_deletes(self, test_db, sample_project):
        """Test delete_project sets is_activated to False"""
        # Act
        ProjectService.delete_project(test_db, sample_project.id)

        # Assert - Project still exists but inactive
        db_project = test_db.query(Project).filter(Project.id == sample_project.id).first()
        assert db_project is not None
        assert db_project.is_activated is False

    def test_delete_project_updates_timestamp(self, test_db, sample_project):
        """Test delete_project updates updated_at timestamp"""
        # Arrange
        original_updated_at = sample_project.updated_at

        # Act
        ProjectService.delete_project(test_db, sample_project.id)

        # Assert
        db_project = test_db.query(Project).filter(Project.id == sample_project.id).first()
        assert db_project.updated_at > original_updated_at

    def test_delete_project_raises_not_found_for_missing_project(self, test_db):
        """Test delete_project raises NotFoundException"""
        # Arrange
        random_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException):
            ProjectService.delete_project(test_db, random_id)

    def test_transaction_rollback_on_error(self, test_db):
        """Test database transaction rolls back on error"""
        # Arrange
        initial_count = test_db.query(Project).count()

        # This test verifies that if an error occurs, changes are rolled back
        # We'll create a project but don't commit manually
        project = Project(
            name="Test",
            developer_name="Dev",
            investor_name="Investor",
            created_by="test@test.com"
        )
        test_db.add(project)
        test_db.rollback()  # Manually rollback

        # Assert - No new project
        assert test_db.query(Project).count() == initial_count
