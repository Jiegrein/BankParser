"""
Unit tests for Bank Accounts service (with mocking)
Tests business logic in isolation without database
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.core.db.models import BankAccount, Project
from app.core.exceptions import BadRequestException, NotFoundException
from app.features.accounts.schemas import (
    BankAccountCreateRequest,
    BankAccountResponse,
    BankAccountUpdateRequest,
)
from app.features.accounts.service import BankAccountService


class TestBankAccountServiceUnit:
    """Unit tests for BankAccountService with mocked database"""

    def test_create_bank_account_verifies_project_exists(self):
        """Test create_bank_account checks if project exists"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # Project not found

        data = BankAccountCreateRequest(
            project_id=uuid4(),
            account_number="1234",
            bank_name="Test Bank",
            account_type="checking",
            created_by="test@test.com",
        )

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            BankAccountService.create_bank_account(mock_db, data)

        assert "not found" in str(exc_info.value.message).lower()

    def test_create_bank_account_calls_database_methods(self):
        """Test create_bank_account calls add, commit, refresh"""
        # Arrange
        mock_db = Mock()
        mock_project_query = Mock()
        project_id = uuid4()

        # Mock project exists
        mock_project = Mock(spec=Project)
        mock_project.id = project_id

        mock_db.query.return_value = mock_project_query
        mock_project_query.filter.return_value = mock_project_query
        mock_project_query.first.return_value = mock_project

        # Mock account creation
        mock_account = Mock(spec=BankAccount)
        mock_account.id = uuid4()
        mock_account.project_id = project_id
        mock_account.account_number = "1234"
        mock_account.bank_name = "Test Bank"
        mock_account.account_type = "checking"
        mock_account.color = None
        mock_account.position_x = None
        mock_account.position_y = None
        mock_account.created_by = "test@test.com"
        mock_account.created_at = datetime.utcnow()
        mock_account.updated_at = None
        mock_account.updated_by = None

        def mock_refresh(obj):
            for key, value in vars(mock_account).items():
                setattr(obj, key, value)

        mock_db.refresh.side_effect = mock_refresh

        data = BankAccountCreateRequest(
            project_id=project_id,
            account_number="1234",
            bank_name="Test Bank",
            account_type="checking",
            created_by="test@test.com",
        )

        # Act
        result = BankAccountService.create_bank_account(mock_db, data)

        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert isinstance(result, BankAccountResponse)

    def test_get_bank_account_raises_not_found_when_missing(self):
        """Test get_bank_account raises NotFoundException when account doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        account_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            BankAccountService.get_bank_account(mock_db, account_id)

        assert "not found" in str(exc_info.value.message).lower()
        assert str(account_id) in exc_info.value.details["account_id"]

    def test_get_bank_account_returns_account_when_found(self):
        """Test get_bank_account returns account when it exists"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        account_id = uuid4()
        project_id = uuid4()

        mock_account = Mock(spec=BankAccount)
        mock_account.id = account_id
        mock_account.project_id = project_id
        mock_account.account_number = "1234"
        mock_account.bank_name = "Test Bank"
        mock_account.account_type = "checking"
        mock_account.color = "#FF5733"
        mock_account.position_x = Decimal("100.5")
        mock_account.position_y = Decimal("200.3")
        mock_account.created_by = "test@test.com"
        mock_account.created_at = datetime.utcnow()
        mock_account.updated_at = None
        mock_account.updated_by = None

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_account

        # Act
        result = BankAccountService.get_bank_account(mock_db, account_id)

        # Assert
        assert isinstance(result, BankAccountResponse)
        assert result.id == account_id
        assert result.account_number == "1234"

    def test_update_bank_account_raises_not_found_when_missing(self):
        """Test update_bank_account raises NotFoundException when account doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        account_id = uuid4()
        data = BankAccountUpdateRequest(bank_name="Updated Bank")

        # Act & Assert
        with pytest.raises(NotFoundException):
            BankAccountService.update_bank_account(mock_db, account_id, data)

    def test_delete_bank_account_raises_not_found_when_missing(self):
        """Test delete_bank_account raises NotFoundException when account doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        account_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException):
            BankAccountService.delete_bank_account(mock_db, account_id)

    def test_pagination_validation_rejects_invalid_page(self):
        """Test get_bank_accounts raises BadRequestException for page < 1"""
        # Arrange
        mock_db = Mock()

        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            BankAccountService.get_bank_accounts(mock_db, page=0, page_size=10)

        assert "page number" in str(exc_info.value.message).lower()

    def test_pagination_validation_rejects_invalid_page_size(self):
        """Test get_bank_accounts raises BadRequestException for page_size > 100"""
        # Arrange
        mock_db = Mock()

        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            BankAccountService.get_bank_accounts(mock_db, page=1, page_size=200)

        assert "page size" in str(exc_info.value.message).lower()


class TestBankAccountSchemasUnit:
    """Unit tests for Pydantic schemas"""

    def test_bank_account_create_request_validates_required_fields(self):
        """Test BankAccountCreateRequest requires all mandatory fields"""
        with pytest.raises(ValueError):
            BankAccountCreateRequest(project_id=uuid4(), account_number="1234")

    def test_bank_account_create_request_strips_whitespace(self):
        """Test BankAccountCreateRequest strips leading/trailing whitespace"""
        data = BankAccountCreateRequest(
            project_id=uuid4(),
            account_number="  1234  ",
            bank_name="  Test Bank  ",
            account_type="  checking  ",
            created_by="  test@test.com  ",
        )

        assert data.account_number == "1234"
        assert data.bank_name == "Test Bank"
        assert data.account_type == "checking"
        assert data.created_by == "test@test.com"

    def test_bank_account_create_request_rejects_empty_strings(self):
        """Test BankAccountCreateRequest rejects empty or whitespace-only strings"""
        with pytest.raises(ValueError) as exc_info:
            BankAccountCreateRequest(
                project_id=uuid4(),
                account_number="   ",  # Whitespace only
                bank_name="Test Bank",
                account_type="checking",
                created_by="test@test.com",
            )

        assert "whitespace" in str(exc_info.value).lower()

    def test_bank_account_update_request_allows_partial_updates(self):
        """Test BankAccountUpdateRequest allows optional fields"""
        # Should not raise - all fields optional
        data = BankAccountUpdateRequest(bank_name="Updated Bank")
        assert data.bank_name == "Updated Bank"
        assert data.account_number is None
        assert data.account_type is None

    def test_bank_account_update_request_strips_whitespace(self):
        """Test BankAccountUpdateRequest strips whitespace from provided fields"""
        data = BankAccountUpdateRequest(
            bank_name="  Updated Bank  ",
            account_number=None,  # Not provided
        )

        assert data.bank_name == "Updated Bank"
        assert data.account_number is None

    def test_bank_account_response_from_attributes(self):
        """Test BankAccountResponse can be created from SQLAlchemy model"""
        # Create a mock account
        account_id = uuid4()
        project_id = uuid4()
        now = datetime.utcnow()

        account = Mock(spec=BankAccount)
        account.id = account_id
        account.project_id = project_id
        account.account_number = "1234"
        account.bank_name = "Test Bank"
        account.account_type = "checking"
        account.color = "#FF5733"
        account.position_x = Decimal("100.5")
        account.position_y = Decimal("200.3")
        account.created_by = "test@test.com"
        account.created_at = now
        account.updated_by = None
        account.updated_at = None

        # Should work with from_attributes=True in Config
        response = BankAccountResponse.model_validate(account)

        assert response.id == account_id
        assert response.account_number == "1234"
        assert response.bank_name == "Test Bank"
