"""
Unit tests for Bank Statement Files service (with mocking)
Tests business logic in isolation without database
"""
from datetime import date, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.core.db.models import BankAccount, BankStatementFile
from app.core.exceptions import BadRequestException, NotFoundException
from app.features.statement_files.schemas import (
    BankStatementFileCreateRequest,
    BankStatementFileResponse,
    BankStatementFileUpdateRequest,
)
from app.features.statement_files.service import BankStatementFileService


class TestBankStatementFileServiceUnit:
    """Unit tests for BankStatementFileService with mocked database"""

    def test_create_statement_file_raises_not_found_for_invalid_bank_account(self):
        """Test create_statement_file raises NotFoundException when bank account doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        bank_account_id = uuid4()
        data = BankStatementFileCreateRequest(
            bank_account_id=bank_account_id,
            file_path="https://storage.blob.core.windows.net/statements/test.pdf",
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            uploaded_by="test@test.com",
        )

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            BankStatementFileService.create_statement_file(mock_db, data)

        assert "bank account" in str(exc_info.value.message).lower()
        assert str(bank_account_id) in exc_info.value.details["bank_account_id"]

    def test_create_statement_file_calls_database_methods(self):
        """Test create_statement_file calls add, commit, refresh"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        bank_account_id = uuid4()

        # Mock bank account exists
        mock_bank_account = Mock(spec=BankAccount)
        mock_bank_account.id = bank_account_id

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_bank_account

        # Mock statement file
        mock_statement_file = Mock(spec=BankStatementFile)
        mock_statement_file.id = uuid4()
        mock_statement_file.bank_account_id = bank_account_id
        mock_statement_file.file_path = "https://storage.blob.core.windows.net/statements/test.pdf"
        mock_statement_file.period_start = date(2024, 1, 1)
        mock_statement_file.period_end = date(2024, 1, 31)
        mock_statement_file.uploaded_by = "test@test.com"
        mock_statement_file.uploaded_at = datetime.utcnow()
        mock_statement_file.updated_at = None
        mock_statement_file.updated_by = None

        def mock_refresh(obj):
            for key, value in vars(mock_statement_file).items():
                setattr(obj, key, value)

        mock_db.refresh.side_effect = mock_refresh

        data = BankStatementFileCreateRequest(
            bank_account_id=bank_account_id,
            file_path="https://storage.blob.core.windows.net/statements/test.pdf",
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            uploaded_by="test@test.com",
        )

        # Act
        result = BankStatementFileService.create_statement_file(mock_db, data)

        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert isinstance(result, BankStatementFileResponse)

    def test_get_statement_file_raises_not_found_when_missing(self):
        """Test get_statement_file raises NotFoundException when statement file doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        statement_file_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            BankStatementFileService.get_statement_file(mock_db, statement_file_id)

        assert "not found" in str(exc_info.value.message).lower()
        assert str(statement_file_id) in exc_info.value.details["statement_file_id"]

    def test_get_statement_file_returns_statement_file_when_found(self):
        """Test get_statement_file returns statement file when it exists"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        statement_file_id = uuid4()

        mock_statement_file = Mock(spec=BankStatementFile)
        mock_statement_file.id = statement_file_id
        mock_statement_file.bank_account_id = uuid4()
        mock_statement_file.file_path = "https://storage.blob.core.windows.net/statements/test.pdf"
        mock_statement_file.period_start = date(2024, 1, 1)
        mock_statement_file.period_end = date(2024, 1, 31)
        mock_statement_file.uploaded_by = "test@test.com"
        mock_statement_file.uploaded_at = datetime.utcnow()
        mock_statement_file.updated_at = None
        mock_statement_file.updated_by = None

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_statement_file

        # Act
        result = BankStatementFileService.get_statement_file(mock_db, statement_file_id)

        # Assert
        assert isinstance(result, BankStatementFileResponse)
        assert result.id == statement_file_id

    def test_update_statement_file_raises_not_found_when_missing(self):
        """Test update_statement_file raises NotFoundException when statement file doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        statement_file_id = uuid4()
        data = BankStatementFileUpdateRequest(
            file_path="https://storage.blob.core.windows.net/statements/updated.pdf"
        )

        # Act & Assert
        with pytest.raises(NotFoundException):
            BankStatementFileService.update_statement_file(mock_db, statement_file_id, data)

    def test_delete_statement_file_raises_not_found_when_missing(self):
        """Test delete_statement_file raises NotFoundException when statement file doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        statement_file_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException):
            BankStatementFileService.delete_statement_file(mock_db, statement_file_id)

    def test_pagination_validation_rejects_invalid_page(self):
        """Test get_statement_files raises BadRequestException for page < 1"""
        # Arrange
        mock_db = Mock()

        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            BankStatementFileService.get_statement_files(mock_db, page=0, page_size=10)

        assert "page number" in str(exc_info.value.message).lower()

    def test_pagination_validation_rejects_invalid_page_size(self):
        """Test get_statement_files raises BadRequestException for page_size > 100"""
        # Arrange
        mock_db = Mock()

        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            BankStatementFileService.get_statement_files(mock_db, page=1, page_size=200)

        assert "page size" in str(exc_info.value.message).lower()


class TestBankStatementFileSchemasUnit:
    """Unit tests for Pydantic schemas"""

    def test_statement_file_create_request_validates_required_fields(self):
        """Test BankStatementFileCreateRequest requires all mandatory fields"""
        with pytest.raises(ValueError):
            BankStatementFileCreateRequest(
                bank_account_id=uuid4(),
                file_path="https://storage.blob.core.windows.net/statements/test.pdf",
                period_start=date(2024, 1, 1),
                # Missing period_end and uploaded_by
            )

    def test_statement_file_create_request_strips_whitespace(self):
        """Test BankStatementFileCreateRequest strips leading/trailing whitespace"""
        data = BankStatementFileCreateRequest(
            bank_account_id=uuid4(),
            file_path="  https://storage.blob.core.windows.net/statements/test.pdf  ",
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            uploaded_by="  test@test.com  ",
        )

        assert data.file_path == "https://storage.blob.core.windows.net/statements/test.pdf"
        assert data.uploaded_by == "test@test.com"

    def test_statement_file_create_request_rejects_empty_strings(self):
        """Test BankStatementFileCreateRequest rejects empty or whitespace-only strings"""
        with pytest.raises(ValueError) as exc_info:
            BankStatementFileCreateRequest(
                bank_account_id=uuid4(),
                file_path="   ",  # Whitespace only
                period_start=date(2024, 1, 1),
                period_end=date(2024, 1, 31),
                uploaded_by="test@test.com",
            )

        assert "whitespace" in str(exc_info.value).lower()

    def test_statement_file_create_request_validates_period(self):
        """Test BankStatementFileCreateRequest validates period_end > period_start"""
        with pytest.raises(ValueError) as exc_info:
            BankStatementFileCreateRequest(
                bank_account_id=uuid4(),
                file_path="https://storage.blob.core.windows.net/statements/test.pdf",
                period_start=date(2024, 1, 31),
                period_end=date(2024, 1, 1),  # Before period_start
                uploaded_by="test@test.com",
            )

        assert "period_end" in str(exc_info.value).lower()

    def test_statement_file_update_request_allows_partial_updates(self):
        """Test BankStatementFileUpdateRequest allows optional fields"""
        # Should not raise - all fields optional
        data = BankStatementFileUpdateRequest(
            file_path="https://storage.blob.core.windows.net/statements/updated.pdf"
        )
        assert data.file_path == "https://storage.blob.core.windows.net/statements/updated.pdf"
        assert data.period_start is None
        assert data.period_end is None

    def test_statement_file_response_from_attributes(self):
        """Test BankStatementFileResponse can be created from SQLAlchemy model"""
        # Create a mock statement file
        statement_file_id = uuid4()
        bank_account_id = uuid4()
        now = datetime.utcnow()

        statement_file = Mock(spec=BankStatementFile)
        statement_file.id = statement_file_id
        statement_file.bank_account_id = bank_account_id
        statement_file.file_path = "https://storage.blob.core.windows.net/statements/test.pdf"
        statement_file.period_start = date(2024, 1, 1)
        statement_file.period_end = date(2024, 1, 31)
        statement_file.uploaded_by = "test@test.com"
        statement_file.uploaded_at = now
        statement_file.updated_at = now
        statement_file.updated_by = None

        # Should work with from_attributes=True in Config
        response = BankStatementFileResponse.model_validate(statement_file)

        assert response.id == statement_file_id
        assert response.bank_account_id == bank_account_id
        assert response.file_path == "https://storage.blob.core.windows.net/statements/test.pdf"
