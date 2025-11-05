"""
Integration tests for Categories service (with real test database)
Tests database queries and transactions with SQLite
"""
from uuid import uuid4

import pytest

from app.core.db.models import Category
from app.core.exceptions import BadRequestException, NotFoundException
from app.features.categories.schemas import (
    CategoryCreateRequest,
    CategoryListResponse,
    CategoryUpdateRequest,
)
from app.features.categories.service import CategoryService


class TestCategoryServiceIntegration:
    """Integration tests for CategoryService with real test database"""

    def test_create_category_saves_to_database(self, test_db):
        """Test create_category persists data to database"""
        # Arrange
        data = CategoryCreateRequest(
            name="Integration Test Category",
            identification_regex=".*INTEGRATION.*",
            color="#00FF00",
            description="Integration test category",
            created_by="integration@test.com",
        )

        # Act
        result = CategoryService.create_category(test_db, data)

        # Assert
        assert result.id is not None
        assert result.name == "Integration Test Category"
        assert result.is_active is True

        # Verify in database
        db_category = (
            test_db.query(Category).filter(Category.id == result.id).first()
        )
        assert db_category is not None
        assert db_category.name == "Integration Test Category"

    def test_create_category_generates_uuid(self, test_db):
        """Test create_category generates valid UUID"""
        # Arrange
        data = CategoryCreateRequest(
            name="UUID Test",
            created_by="test@test.com",
        )

        # Act
        result = CategoryService.create_category(test_db, data)

        # Assert
        assert result.id is not None
        assert isinstance(result.id, type(uuid4()))

    def test_create_category_sets_timestamps(self, test_db):
        """Test create_category sets created_at and updated_at"""
        # Arrange
        data = CategoryCreateRequest(
            name="Timestamp Test",
            created_by="test@test.com",
        )

        # Act
        result = CategoryService.create_category(test_db, data)

        # Assert
        assert result.created_at is not None
        # updated_at has a default value in the model, so it will be set on creation
        assert result.updated_at is not None
        assert result.updated_by is None

    def test_get_category_retrieves_existing_category(self, test_db, sample_category):
        """Test get_category retrieves existing category from database"""
        # Act
        result = CategoryService.get_category(test_db, sample_category.id)

        # Assert
        assert result.id == sample_category.id
        assert result.name == sample_category.name
        assert result.description == sample_category.description

    def test_get_category_raises_not_found_for_missing_category(self, test_db):
        """Test get_category raises NotFoundException for non-existent category"""
        # Arrange
        random_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            CategoryService.get_category(test_db, random_id)

        assert str(random_id) in exc_info.value.details["category_id"]

    def test_get_categories_returns_paginated_list(self, test_db, multiple_categories):
        """Test get_categories returns paginated results"""
        # Act
        result = CategoryService.get_categories(test_db, page=1, page_size=10)

        # Assert
        assert isinstance(result, CategoryListResponse)
        assert result.total == 5
        assert len(result.items) == 5
        assert result.page == 1
        assert result.page_size == 10
        assert result.total_pages == 1

    def test_get_categories_pagination_works_correctly(
        self, test_db, multiple_categories
    ):
        """Test get_categories pagination splits results correctly"""
        # Act - Page 1
        page1 = CategoryService.get_categories(test_db, page=1, page_size=2)
        # Act - Page 2
        page2 = CategoryService.get_categories(test_db, page=2, page_size=2)

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

    def test_get_categories_filters_by_is_active(self, test_db, multiple_categories):
        """Test get_categories filters by is_active status"""
        # Act - Active only
        active_result = CategoryService.get_categories(
            test_db, page=1, page_size=10, is_active=True
        )

        # Act - Inactive only
        inactive_result = CategoryService.get_categories(
            test_db, page=1, page_size=10, is_active=False
        )

        # Assert
        assert active_result.total == 3  # Categories 0, 2, 4 are active
        assert inactive_result.total == 2  # Categories 1, 3 are inactive

        for item in active_result.items:
            assert item.is_active is True

        for item in inactive_result.items:
            assert item.is_active is False

    def test_get_categories_search_by_name(self, test_db, multiple_categories):
        """Test get_categories searches by category name"""
        # Act
        result = CategoryService.get_categories(
            test_db, page=1, page_size=10, search="Category 3"
        )

        # Assert
        assert result.total == 1
        assert result.items[0].name == "Category 3"

    def test_get_categories_search_by_description(self, test_db, multiple_categories):
        """Test get_categories searches by description"""
        # Act
        result = CategoryService.get_categories(
            test_db, page=1, page_size=10, search="Category 2 description"
        )

        # Assert
        assert result.total == 1
        assert result.items[0].name == "Category 2"

    def test_get_categories_search_is_case_insensitive(
        self, test_db, multiple_categories
    ):
        """Test get_categories search is case-insensitive"""
        # Act
        result = CategoryService.get_categories(
            test_db, page=1, page_size=10, search="category"
        )

        # Assert - Should find all categories (all have "Category" in name)
        assert result.total == 5

    def test_get_categories_orders_by_created_at_desc(
        self, test_db, multiple_categories
    ):
        """Test get_categories returns newest categories first"""
        # Act
        result = CategoryService.get_categories(test_db, page=1, page_size=10)

        # Assert - Newest first
        for i in range(len(result.items) - 1):
            assert result.items[i].created_at >= result.items[i + 1].created_at

    def test_update_category_updates_database(self, test_db, sample_category):
        """Test update_category persists changes to database"""
        # Arrange
        data = CategoryUpdateRequest(
            name="Updated Category Name",
            color="#0000FF",
            updated_by="updater@test.com",
        )

        # Act
        result = CategoryService.update_category(test_db, sample_category.id, data)

        # Assert
        assert result.name == "Updated Category Name"
        assert result.color == "#0000FF"
        assert result.updated_by == "updater@test.com"
        assert result.updated_at > sample_category.created_at

        # Verify in database
        db_category = (
            test_db.query(Category).filter(Category.id == sample_category.id).first()
        )
        assert db_category.name == "Updated Category Name"

    def test_update_category_partial_update_preserves_other_fields(
        self, test_db, sample_category
    ):
        """Test update_category only updates provided fields"""
        # Arrange
        original_name = sample_category.name
        data = CategoryUpdateRequest(color="#FFFFFF")

        # Act
        result = CategoryService.update_category(test_db, sample_category.id, data)

        # Assert
        assert result.color == "#FFFFFF"
        assert result.name == original_name  # Unchanged

    def test_update_category_raises_not_found_for_missing_category(self, test_db):
        """Test update_category raises NotFoundException"""
        # Arrange
        random_id = uuid4()
        data = CategoryUpdateRequest(name="Updated")

        # Act & Assert
        with pytest.raises(NotFoundException):
            CategoryService.update_category(test_db, random_id, data)

    def test_delete_category_soft_deletes(self, test_db, sample_category):
        """Test delete_category sets is_active to False"""
        # Act
        CategoryService.delete_category(test_db, sample_category.id)

        # Assert - Category still exists but inactive
        db_category = (
            test_db.query(Category).filter(Category.id == sample_category.id).first()
        )
        assert db_category is not None
        assert db_category.is_active is False

    def test_delete_category_updates_timestamp(self, test_db, sample_category):
        """Test delete_category updates updated_at timestamp"""
        # Arrange
        original_updated_at = sample_category.updated_at

        # Act
        CategoryService.delete_category(test_db, sample_category.id)

        # Assert
        db_category = (
            test_db.query(Category).filter(Category.id == sample_category.id).first()
        )
        assert db_category.updated_at > original_updated_at

    def test_delete_category_raises_not_found_for_missing_category(self, test_db):
        """Test delete_category raises NotFoundException"""
        # Arrange
        random_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException):
            CategoryService.delete_category(test_db, random_id)

    def test_pagination_validation_page_zero(self, test_db):
        """Test get_categories rejects page=0"""
        # Act & Assert
        with pytest.raises(BadRequestException):
            CategoryService.get_categories(test_db, page=0, page_size=10)

    def test_pagination_validation_page_size_over_100(self, test_db):
        """Test get_categories rejects page_size > 100"""
        # Act & Assert
        with pytest.raises(BadRequestException):
            CategoryService.get_categories(test_db, page=1, page_size=200)

    def test_transaction_rollback_on_error(self, test_db):
        """Test database transaction rolls back on error"""
        # Arrange
        initial_count = test_db.query(Category).count()

        # This test verifies that if an error occurs, changes are rolled back
        # We'll create a category but don't commit manually
        category = Category(
            name="Test",
            is_active=True,
            created_by="test@test.com",
        )
        test_db.add(category)
        test_db.rollback()  # Manually rollback

        # Assert - No new category
        assert test_db.query(Category).count() == initial_count
