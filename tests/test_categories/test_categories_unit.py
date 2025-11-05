"""
Unit tests for Categories service (with mocking)
Tests business logic in isolation without database
"""
from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.core.db.models import Category
from app.core.exceptions import BadRequestException, NotFoundException
from app.features.categories.schemas import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
)
from app.features.categories.service import CategoryService


class TestCategoryServiceUnit:
    """Unit tests for CategoryService with mocked database"""

    def test_create_category_calls_database_methods(self):
        """Test create_category calls add, commit, refresh"""
        # Arrange
        mock_db = Mock()
        mock_category = Mock(spec=Category)
        mock_category.id = uuid4()
        mock_category.name = "Test Category"
        mock_category.identification_regex = ".*TEST.*"
        mock_category.color = "#FF5733"
        mock_category.is_active = True
        mock_category.description = "Test description"
        mock_category.created_by = "test@test.com"
        mock_category.created_at = datetime.utcnow()
        mock_category.updated_at = None
        mock_category.updated_by = None

        def mock_refresh(obj):
            for key, value in vars(mock_category).items():
                setattr(obj, key, value)

        mock_db.refresh.side_effect = mock_refresh

        data = CategoryCreateRequest(
            name="Test Category",
            identification_regex=".*TEST.*",
            color="#FF5733",
            description="Test description",
            created_by="test@test.com",
        )

        # Act
        result = CategoryService.create_category(mock_db, data)

        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert isinstance(result, CategoryResponse)

    def test_get_category_raises_not_found_when_missing(self):
        """Test get_category raises NotFoundException when category doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        category_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            CategoryService.get_category(mock_db, category_id)

        assert "not found" in str(exc_info.value.message).lower()
        assert str(category_id) in exc_info.value.details["category_id"]

    def test_get_category_returns_category_when_found(self):
        """Test get_category returns category when it exists"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        category_id = uuid4()

        mock_category = Mock(spec=Category)
        mock_category.id = category_id
        mock_category.name = "Test Category"
        mock_category.identification_regex = ".*TEST.*"
        mock_category.color = "#FF5733"
        mock_category.is_active = True
        mock_category.description = "Test description"
        mock_category.created_by = "test@test.com"
        mock_category.created_at = datetime.utcnow()
        mock_category.updated_at = None
        mock_category.updated_by = None

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_category

        # Act
        result = CategoryService.get_category(mock_db, category_id)

        # Assert
        assert isinstance(result, CategoryResponse)
        assert result.id == category_id
        assert result.name == "Test Category"

    def test_update_category_raises_not_found_when_missing(self):
        """Test update_category raises NotFoundException when category doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        category_id = uuid4()
        data = CategoryUpdateRequest(name="Updated Category")

        # Act & Assert
        with pytest.raises(NotFoundException):
            CategoryService.update_category(mock_db, category_id, data)

    def test_delete_category_raises_not_found_when_missing(self):
        """Test delete_category raises NotFoundException when category doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        category_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException):
            CategoryService.delete_category(mock_db, category_id)

    def test_pagination_validation_rejects_invalid_page(self):
        """Test get_categories raises BadRequestException for page < 1"""
        # Arrange
        mock_db = Mock()

        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            CategoryService.get_categories(mock_db, page=0, page_size=10)

        assert "page number" in str(exc_info.value.message).lower()

    def test_pagination_validation_rejects_invalid_page_size(self):
        """Test get_categories raises BadRequestException for page_size > 100"""
        # Arrange
        mock_db = Mock()

        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            CategoryService.get_categories(mock_db, page=1, page_size=200)

        assert "page size" in str(exc_info.value.message).lower()


class TestCategorySchemasUnit:
    """Unit tests for Pydantic schemas"""

    def test_category_create_request_validates_required_fields(self):
        """Test CategoryCreateRequest requires all mandatory fields"""
        with pytest.raises(ValueError):
            CategoryCreateRequest(name="Test")

    def test_category_create_request_strips_whitespace(self):
        """Test CategoryCreateRequest strips leading/trailing whitespace"""
        data = CategoryCreateRequest(
            name="  Test Category  ",
            created_by="  test@test.com  ",
        )

        assert data.name == "Test Category"
        assert data.created_by == "test@test.com"

    def test_category_create_request_rejects_empty_strings(self):
        """Test CategoryCreateRequest rejects empty or whitespace-only strings"""
        with pytest.raises(ValueError) as exc_info:
            CategoryCreateRequest(
                name="   ",  # Whitespace only
                created_by="test@test.com",
            )

        assert "whitespace" in str(exc_info.value).lower()

    def test_category_update_request_allows_partial_updates(self):
        """Test CategoryUpdateRequest allows optional fields"""
        # Should not raise - all fields optional
        data = CategoryUpdateRequest(name="Updated Category")
        assert data.name == "Updated Category"
        assert data.color is None
        assert data.description is None

    def test_category_update_request_strips_whitespace(self):
        """Test CategoryUpdateRequest strips whitespace from provided fields"""
        data = CategoryUpdateRequest(
            name="  Updated Category  ",
            color=None,  # Not provided
        )

        assert data.name == "Updated Category"
        assert data.color is None

    def test_category_response_from_attributes(self):
        """Test CategoryResponse can be created from SQLAlchemy model"""
        # Create a mock category
        category_id = uuid4()
        now = datetime.utcnow()

        category = Mock(spec=Category)
        category.id = category_id
        category.name = "Test Category"
        category.identification_regex = ".*TEST.*"
        category.color = "#FF5733"
        category.is_active = True
        category.description = "Test description"
        category.created_by = "test@test.com"
        category.created_at = now
        category.updated_by = None
        category.updated_at = now

        # Should work with from_attributes=True in Config
        response = CategoryResponse.model_validate(category)

        assert response.id == category_id
        assert response.name == "Test Category"
        assert response.is_active is True
