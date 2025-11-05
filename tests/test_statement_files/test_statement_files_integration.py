"""
Integration tests for Bank Statement Files service (with real test database)
Tests database queries and transactions with SQLite
"""
from datetime import date
from uuid import uuid4

import pytest

from app.core.db.models import BankStatementFile
from app.core.exceptions import BadRequestException, NotFoundException
from app.features.statement_files.schemas import (
    BankStatementFileCreateRequest,
    BankStatementFileListResponse,
    BankStatementFileUpdateRequest,
)
from app.features.statement_files.service import BankStatementFileService


class TestBankStatementFileServiceIntegration:
    """Integration tests for BankStatementFileService with real test database"""

    def test_create_statement_file_saves_to_database(
        self, test_db, sample_bank_account
    ):
        """Test create_statement_file persists data to database"""
        # Arrange
        data = BankStatementFileCreateRequest(
            bank_account_id=sample_bank_account.id,
            file_path="https://storage.blob.core.windows.net/statements/integration_test.pdf",
            period_start=date(2024, 2, 1),
            period_end=date(2024, 2, 29),
            uploaded_by="integration@test.com",
        )

        # Act
        result = BankStatementFileService.create_statement_file(test_db, data)

        # Assert
        assert result.id is not None
        assert result.bank_account_id == sample_bank_account.id
        assert result.file_path == "https://storage.blob.core.windows.net/statements/integration_test.pdf"
        assert result.period_start == date(2024, 2, 1)
        assert result.period_end == date(2024, 2, 29)

        # Verify in database
        db_statement_file = (
            test_db.query(BankStatementFile)
            .filter(BankStatementFile.id == result.id)
            .first()
        )
        assert db_statement_file is not None
        assert db_statement_file.file_path == "https://storage.blob.core.windows.net/statements/integration_test.pdf"

    def test_create_statement_file_raises_not_found_for_invalid_bank_account(
        self, test_db
    ):
        """Test create_statement_file raises NotFoundException for non-existent bank account"""
        # Arrange
        random_bank_account_id = uuid4()
        data = BankStatementFileCreateRequest(
            bank_account_id=random_bank_account_id,
            file_path="https://storage.blob.core.windows.net/statements/test.pdf",
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            uploaded_by="test@test.com",
        )

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            BankStatementFileService.create_statement_file(test_db, data)

        assert "bank account" in str(exc_info.value.message).lower()

    def test_create_statement_file_generates_uuid(self, test_db, sample_bank_account):
        """Test create_statement_file generates valid UUID"""
        # Arrange
        data = BankStatementFileCreateRequest(
            bank_account_id=sample_bank_account.id,
            file_path="https://storage.blob.core.windows.net/statements/uuid_test.pdf",
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            uploaded_by="test@test.com",
        )

        # Act
        result = BankStatementFileService.create_statement_file(test_db, data)

        # Assert
        assert result.id is not None
        assert isinstance(result.id, type(uuid4()))

    def test_create_statement_file_sets_timestamps(self, test_db, sample_bank_account):
        """Test create_statement_file sets uploaded_at and updated_at"""
        # Arrange
        data = BankStatementFileCreateRequest(
            bank_account_id=sample_bank_account.id,
            file_path="https://storage.blob.core.windows.net/statements/timestamp_test.pdf",
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            uploaded_by="test@test.com",
        )

        # Act
        result = BankStatementFileService.create_statement_file(test_db, data)

        # Assert
        assert result.uploaded_at is not None
        # updated_at has a default value in the model, so it will be set on creation
        assert result.updated_at is not None
        assert result.updated_by is None

    def test_get_statement_file_retrieves_existing_statement_file(
        self, test_db, sample_statement_file
    ):
        """Test get_statement_file retrieves existing statement file from database"""
        # Act
        result = BankStatementFileService.get_statement_file(
            test_db, sample_statement_file.id
        )

        # Assert
        assert result.id == sample_statement_file.id
        assert result.file_path == sample_statement_file.file_path
        assert result.period_start == sample_statement_file.period_start
        assert result.period_end == sample_statement_file.period_end

    def test_get_statement_file_raises_not_found_for_missing_statement_file(
        self, test_db
    ):
        """Test get_statement_file raises NotFoundException for non-existent statement file"""
        # Arrange
        random_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            BankStatementFileService.get_statement_file(test_db, random_id)

        assert str(random_id) in exc_info.value.details["statement_file_id"]

    def test_get_statement_files_returns_paginated_list(
        self, test_db, multiple_statement_files
    ):
        """Test get_statement_files returns paginated results"""
        # Act
        result = BankStatementFileService.get_statement_files(
            test_db, page=1, page_size=10
        )

        # Assert
        assert isinstance(result, BankStatementFileListResponse)
        assert result.total == 5
        assert len(result.items) == 5
        assert result.page == 1
        assert result.page_size == 10
        assert result.total_pages == 1

    def test_get_statement_files_pagination_works_correctly(
        self, test_db, multiple_statement_files
    ):
        """Test get_statement_files pagination splits results correctly"""
        # Act - Page 1
        page1 = BankStatementFileService.get_statement_files(
            test_db, page=1, page_size=2
        )
        # Act - Page 2
        page2 = BankStatementFileService.get_statement_files(
            test_db, page=2, page_size=2
        )

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

    def test_get_statement_files_filters_by_bank_account_id(
        self, test_db, sample_bank_account, sample_project
    ):
        """Test get_statement_files filters by bank_account_id"""
        # Arrange - Create another bank account with statement files
        from app.core.db.models import BankAccount

        other_account = BankAccount(
            project_id=sample_project.id,
            account_number="9999",
            bank_name="Other Bank",
            account_type="checking",
            created_by="test@test.com",
        )
        test_db.add(other_account)
        test_db.commit()
        test_db.refresh(other_account)

        # Create statement files for both accounts
        sf1 = BankStatementFile(
            bank_account_id=sample_bank_account.id,
            file_path="https://storage.blob.core.windows.net/statements/account1_statement.pdf",
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            uploaded_by="test@test.com",
        )
        sf2 = BankStatementFile(
            bank_account_id=other_account.id,
            file_path="https://storage.blob.core.windows.net/statements/account2_statement.pdf",
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            uploaded_by="test@test.com",
        )
        test_db.add(sf1)
        test_db.add(sf2)
        test_db.commit()

        # Act - Filter by first account
        result = BankStatementFileService.get_statement_files(
            test_db, page=1, page_size=10, bank_account_id=sample_bank_account.id
        )

        # Assert
        assert result.total == 1
        assert result.items[0].bank_account_id == sample_bank_account.id

    def test_get_statement_files_search_by_file_path(
        self, test_db, multiple_statement_files
    ):
        """Test get_statement_files searches by file_path"""
        # Act
        result = BankStatementFileService.get_statement_files(
            test_db, page=1, page_size=10, search="statement_3"
        )

        # Assert
        assert result.total == 1
        assert "statement_3" in result.items[0].file_path

    def test_get_statement_files_search_is_case_insensitive(
        self, test_db, multiple_statement_files
    ):
        """Test get_statement_files search is case-insensitive"""
        # Act
        result = BankStatementFileService.get_statement_files(
            test_db, page=1, page_size=10, search="STATEMENT"
        )

        # Assert - Should find all statement files (all have "statement" in file_path)
        assert result.total == 5

    def test_get_statement_files_orders_by_uploaded_at_desc(
        self, test_db, multiple_statement_files
    ):
        """Test get_statement_files returns newest statement files first"""
        # Act
        result = BankStatementFileService.get_statement_files(
            test_db, page=1, page_size=10
        )

        # Assert - Newest first
        for i in range(len(result.items) - 1):
            assert result.items[i].uploaded_at >= result.items[i + 1].uploaded_at

    def test_update_statement_file_updates_database(
        self, test_db, sample_statement_file
    ):
        """Test update_statement_file persists changes to database"""
        # Arrange
        data = BankStatementFileUpdateRequest(
            file_path="https://storage.blob.core.windows.net/statements/updated_statement.pdf",
            updated_by="updater@test.com",
        )

        # Act
        result = BankStatementFileService.update_statement_file(
            test_db, sample_statement_file.id, data
        )

        # Assert
        assert result.file_path == "https://storage.blob.core.windows.net/statements/updated_statement.pdf"
        assert result.updated_by == "updater@test.com"
        assert result.updated_at > sample_statement_file.uploaded_at

        # Verify in database
        db_statement_file = (
            test_db.query(BankStatementFile)
            .filter(BankStatementFile.id == sample_statement_file.id)
            .first()
        )
        assert db_statement_file.file_path == "https://storage.blob.core.windows.net/statements/updated_statement.pdf"

    def test_update_statement_file_partial_update_preserves_other_fields(
        self, test_db, sample_statement_file
    ):
        """Test update_statement_file only updates provided fields"""
        # Arrange
        original_file_path = sample_statement_file.file_path
        data = BankStatementFileUpdateRequest(
            period_start=date(2024, 3, 1), period_end=date(2024, 3, 31)
        )

        # Act
        result = BankStatementFileService.update_statement_file(
            test_db, sample_statement_file.id, data
        )

        # Assert
        assert result.period_start == date(2024, 3, 1)
        assert result.period_end == date(2024, 3, 31)
        assert result.file_path == original_file_path  # Unchanged

    def test_update_statement_file_raises_not_found_for_missing_statement_file(
        self, test_db
    ):
        """Test update_statement_file raises NotFoundException"""
        # Arrange
        random_id = uuid4()
        data = BankStatementFileUpdateRequest(
            file_path="https://storage.blob.core.windows.net/statements/updated.pdf"
        )

        # Act & Assert
        with pytest.raises(NotFoundException):
            BankStatementFileService.update_statement_file(test_db, random_id, data)

    def test_delete_statement_file_removes_from_database(
        self, test_db, sample_statement_file
    ):
        """Test delete_statement_file removes record from database"""
        # Act
        BankStatementFileService.delete_statement_file(
            test_db, sample_statement_file.id
        )

        # Assert - Statement file should not exist
        db_statement_file = (
            test_db.query(BankStatementFile)
            .filter(BankStatementFile.id == sample_statement_file.id)
            .first()
        )
        assert db_statement_file is None

    def test_delete_statement_file_raises_not_found_for_missing_statement_file(
        self, test_db
    ):
        """Test delete_statement_file raises NotFoundException"""
        # Arrange
        random_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException):
            BankStatementFileService.delete_statement_file(test_db, random_id)

    def test_pagination_validation_page_zero(self, test_db):
        """Test get_statement_files rejects page=0"""
        # Act & Assert
        with pytest.raises(BadRequestException):
            BankStatementFileService.get_statement_files(
                test_db, page=0, page_size=10
            )

    def test_pagination_validation_page_size_over_100(self, test_db):
        """Test get_statement_files rejects page_size > 100"""
        # Act & Assert
        with pytest.raises(BadRequestException):
            BankStatementFileService.get_statement_files(
                test_db, page=1, page_size=200
            )

    def test_transaction_rollback_on_error(self, test_db, sample_bank_account):
        """Test database transaction rolls back on error"""
        # Arrange
        initial_count = test_db.query(BankStatementFile).count()

        # This test verifies that if an error occurs, changes are rolled back
        # We'll create a statement file but don't commit manually
        statement_file = BankStatementFile(
            bank_account_id=sample_bank_account.id,
            file_path="https://storage.blob.core.windows.net/statements/test.pdf",
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            uploaded_by="test@test.com",
        )
        test_db.add(statement_file)
        test_db.rollback()  # Manually rollback

        # Assert - No new statement file
        assert test_db.query(BankStatementFile).count() == initial_count
