"""
Unit tests for Projects service (with mocking)
Tests business logic in isolation without database
"""
import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from datetime import datetime

from app.features.projects.service import ProjectService
from app.features.projects.schemas import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse
)
from app.core.db.models import Project
from app.core.exceptions import NotFoundException, BadRequestException


class TestProjectServiceUnit:
    """Unit tests for ProjectService with mocked database"""

    def test_create_project_calls_database_methods(self):
        """Test create_project calls add, commit, refresh"""
        # Arrange
        mock_db = Mock()
        mock_project = Mock(spec=Project)
        mock_project.id = uuid4()
        mock_project.name = "Test Project"
        mock_project.developer_name = "Test Dev"
        mock_project.investor_name = "Test Investor"
        mock_project.is_activated = True
        mock_project.remarks = "Test remarks"
        mock_project.created_by = "test@test.com"
        mock_project.created_at = datetime.utcnow()
        mock_project.updated_at = datetime.utcnow()
        mock_project.updated_by = None

        data = ProjectCreateRequest(
            name="Test Project",
            developer_name="Test Dev",
            investor_name="Test Investor",
            remarks="Test remarks",
            created_by="test@test.com"
        )

        # Mock the refresh to set attributes
        def mock_refresh(obj):
            for key, value in vars(mock_project).items():
                setattr(obj, key, value)

        mock_db.refresh.side_effect = mock_refresh

        # Act
        result = ProjectService.create_project(mock_db, data)

        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert isinstance(result, ProjectResponse)

    def test_get_project_raises_not_found_when_project_missing(self):
        """Test get_project raises NotFoundException when project doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        project_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            ProjectService.get_project(mock_db, project_id)

        assert "not found" in str(exc_info.value.message).lower()
        assert str(project_id) in exc_info.value.details["project_id"]

    def test_get_project_returns_project_when_found(self):
        """Test get_project returns project when it exists"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        project_id = uuid4()

        mock_project = Mock(spec=Project)
        mock_project.id = project_id
        mock_project.name = "Test Project"
        mock_project.developer_name = "Test Dev"
        mock_project.investor_name = "Test Investor"
        mock_project.is_activated = True
        mock_project.remarks = "Test"
        mock_project.created_by = "test@test.com"
        mock_project.created_at = datetime.utcnow()
        mock_project.updated_at = datetime.utcnow()
        mock_project.updated_by = None

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_project

        # Act
        result = ProjectService.get_project(mock_db, project_id)

        # Assert
        assert isinstance(result, ProjectResponse)
        assert result.id == project_id
        assert result.name == "Test Project"

    def test_update_project_raises_not_found_when_missing(self):
        """Test update_project raises NotFoundException when project doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        project_id = uuid4()
        data = ProjectUpdateRequest(name="Updated Name")

        # Act & Assert
        with pytest.raises(NotFoundException):
            ProjectService.update_project(mock_db, project_id, data)

    def test_delete_project_raises_not_found_when_missing(self):
        """Test delete_project raises NotFoundException when project doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        project_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException):
            ProjectService.delete_project(mock_db, project_id)

    def test_pagination_validation_rejects_invalid_page(self):
        """Test get_projects raises BadRequestException for page < 1"""
        # Arrange
        mock_db = Mock()

        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            ProjectService.get_projects(mock_db, page=0, page_size=10)

        assert "page number" in str(exc_info.value.message).lower()

    def test_pagination_validation_rejects_invalid_page_size(self):
        """Test get_projects raises BadRequestException for page_size > 100"""
        # Arrange
        mock_db = Mock()

        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            ProjectService.get_projects(mock_db, page=1, page_size=200)

        assert "page size" in str(exc_info.value.message).lower()


class TestProjectSchemasUnit:
    """Unit tests for Pydantic schemas"""

    def test_project_create_request_validates_required_fields(self):
        """Test ProjectCreateRequest requires all mandatory fields"""
        with pytest.raises(ValueError):
            ProjectCreateRequest(name="Test")

    def test_project_create_request_strips_whitespace(self):
        """Test ProjectCreateRequest strips leading/trailing whitespace"""
        data = ProjectCreateRequest(
            name="  Test Project  ",
            developer_name="  Dev Corp  ",
            investor_name="  Investor  ",
            created_by="  test@test.com  "
        )

        assert data.name == "Test Project"
        assert data.developer_name == "Dev Corp"
        assert data.investor_name == "Investor"
        assert data.created_by == "test@test.com"

    def test_project_create_request_rejects_empty_strings(self):
        """Test ProjectCreateRequest rejects empty or whitespace-only strings"""
        with pytest.raises(ValueError) as exc_info:
            ProjectCreateRequest(
                name="   ",  # Whitespace only
                developer_name="Dev",
                investor_name="Investor",
                created_by="test@test.com"
            )

        assert "whitespace" in str(exc_info.value).lower()

    def test_project_update_request_allows_partial_updates(self):
        """Test ProjectUpdateRequest allows optional fields"""
        # Should not raise - all fields optional
        data = ProjectUpdateRequest(name="Updated Name")
        assert data.name == "Updated Name"
        assert data.developer_name is None
        assert data.investor_name is None

    def test_project_update_request_strips_whitespace(self):
        """Test ProjectUpdateRequest strips whitespace from provided fields"""
        data = ProjectUpdateRequest(
            name="  Updated  ",
            developer_name=None,  # Not provided
        )

        assert data.name == "Updated"
        assert data.developer_name is None

    def test_project_response_from_attributes(self):
        """Test ProjectResponse can be created from SQLAlchemy model"""
        # Create a mock project
        project_id = uuid4()
        now = datetime.utcnow()

        project = Mock(spec=Project)
        project.id = project_id
        project.name = "Test"
        project.developer_name = "Dev"
        project.investor_name = "Investor"
        project.is_activated = True
        project.remarks = "Remarks"
        project.created_by = "test@test.com"
        project.created_at = now
        project.updated_by = None
        project.updated_at = now

        # Should work with from_attributes=True in Config
        response = ProjectResponse.model_validate(project)

        assert response.id == project_id
        assert response.name == "Test"
        assert response.is_activated is True
