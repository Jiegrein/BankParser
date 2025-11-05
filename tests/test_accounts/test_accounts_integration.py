"""
Integration tests for Bank Accounts service (with real test database)
Tests database queries and transactions with SQLite
"""

from uuid import uuid4

import pytest

from app.core.db.models import BankAccount, Project
from app.core.exceptions import NotFoundException
from app.features.accounts.schemas import (
    BankAccountCreateRequest,
    BankAccountListResponse,
    BankAccountUpdateRequest,
)
from app.features.accounts.service import BankAccountService


class TestBankAccountServiceIntegration:
    """Integration tests for BankAccountService with real test database"""

    def test_create_bank_account_saves_to_database(self, test_db, sample_project):
        """Test create_bank_account persists data to database"""
        # Arrange
        data = BankAccountCreateRequest(
            project_id=sample_project.id,
            account_number="5678",
            bank_name="Integration Bank",
            account_type="savings",
            color="#00FF00",
            created_by="integration@test.com",
        )

        # Act
        result = BankAccountService.create_bank_account(test_db, data)

        # Assert
        assert result.id is not None
        assert result.account_number == "5678"
        assert result.bank_name == "Integration Bank"

        # Verify in database
        db_account = (
            test_db.query(BankAccount).filter(BankAccount.id == result.id).first()
        )
        assert db_account is not None
        assert db_account.account_number == "5678"
        assert db_account.bank_name == "Integration Bank"

    def test_create_bank_account_validates_project_exists(self, test_db):
        """Test create_bank_account raises error if project doesn't exist"""
        # Arrange
        fake_project_id = uuid4()
        data = BankAccountCreateRequest(
            project_id=fake_project_id,
            account_number="1234",
            bank_name="Test Bank",
            account_type="checking",
            created_by="test@test.com",
        )

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            BankAccountService.create_bank_account(test_db, data)

        assert str(fake_project_id) in exc_info.value.details["project_id"]

    def test_create_bank_account_generates_uuid(self, test_db, sample_project):
        """Test create_bank_account generates valid UUID"""
        # Arrange
        data = BankAccountCreateRequest(
            project_id=sample_project.id,
            account_number="1234",
            bank_name="UUID Test Bank",
            account_type="checking",
            created_by="test@test.com",
        )

        # Act
        result = BankAccountService.create_bank_account(test_db, data)

        # Assert
        assert result.id is not None
        assert isinstance(result.id, type(uuid4()))

    def test_create_bank_account_sets_timestamps(self, test_db, sample_project):
        """Test create_bank_account sets created_at and updated_at"""
        # Arrange
        data = BankAccountCreateRequest(
            project_id=sample_project.id,
            account_number="1234",
            bank_name="Timestamp Test",
            account_type="checking",
            created_by="test@test.com",
        )

        # Act
        result = BankAccountService.create_bank_account(test_db, data)

        # Assert
        assert result.created_at is not None
        # updated_at has a default value in the model, so it will be set on creation
        assert result.updated_at is not None
        assert result.updated_by is None

    def test_get_bank_account_retrieves_existing_account(
        self, test_db, sample_bank_account
    ):
        """Test get_bank_account retrieves existing account from database"""
        # Act
        result = BankAccountService.get_bank_account(test_db, sample_bank_account.id)

        # Assert
        assert result.id == sample_bank_account.id
        assert result.account_number == sample_bank_account.account_number
        assert result.bank_name == sample_bank_account.bank_name

    def test_get_bank_account_raises_not_found_for_missing_account(self, test_db):
        """Test get_bank_account raises NotFoundException for non-existent account"""
        # Arrange
        random_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            BankAccountService.get_bank_account(test_db, random_id)

        assert str(random_id) in exc_info.value.details["account_id"]

    def test_get_bank_accounts_returns_paginated_list(
        self, test_db, multiple_bank_accounts
    ):
        """Test get_bank_accounts returns paginated results"""
        # Act
        result = BankAccountService.get_bank_accounts(test_db, page=1, page_size=10)

        # Assert
        assert isinstance(result, BankAccountListResponse)
        assert result.total == 5
        assert len(result.items) == 5
        assert result.page == 1
        assert result.page_size == 10
        assert result.total_pages == 1

    def test_get_bank_accounts_pagination_works_correctly(
        self, test_db, multiple_bank_accounts
    ):
        """Test get_bank_accounts pagination splits results correctly"""
        # Act - Page 1
        page1 = BankAccountService.get_bank_accounts(test_db, page=1, page_size=2)
        # Act - Page 2
        page2 = BankAccountService.get_bank_accounts(test_db, page=2, page_size=2)

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

    def test_get_bank_accounts_filters_by_project_id(self, test_db, sample_project):
        """Test get_bank_accounts filters by project_id"""
        # Arrange - Create another project
        other_project = Project(
            name="Other Project",
            developer_name="Other Dev",
            investor_name="Other Investor",
            created_by="other@test.com",
            is_activated=True,
        )
        test_db.add(other_project)
        test_db.commit()
        test_db.refresh(other_project)

        # Create accounts for both projects
        account1 = BankAccount(
            project_id=sample_project.id,
            account_number="1111",
            bank_name="Bank 1",
            account_type="checking",
            created_by="test@test.com",
        )
        account2 = BankAccount(
            project_id=other_project.id,
            account_number="2222",
            bank_name="Bank 2",
            account_type="savings",
            created_by="test@test.com",
        )
        test_db.add(account1)
        test_db.add(account2)
        test_db.commit()

        # Act - Filter by sample_project
        result = BankAccountService.get_bank_accounts(
            test_db, page=1, page_size=10, project_id=sample_project.id
        )

        # Assert
        assert result.total == 1
        assert result.items[0].project_id == sample_project.id
        assert result.items[0].account_number == "1111"

    def test_get_bank_accounts_search_by_bank_name(
        self, test_db, multiple_bank_accounts
    ):
        """Test get_bank_accounts searches by bank name"""
        # Act
        result = BankAccountService.get_bank_accounts(
            test_db, page=1, page_size=10, search="Bank 3"
        )

        # Assert
        assert result.total == 1
        assert result.items[0].bank_name == "Bank 3"

    def test_get_bank_accounts_search_by_account_number(
        self, test_db, multiple_bank_accounts
    ):
        """Test get_bank_accounts searches by account number"""
        # Act
        result = BankAccountService.get_bank_accounts(
            test_db, page=1, page_size=10, search="1232"
        )

        # Assert
        assert result.total == 1
        assert result.items[0].account_number == "1232"

    def test_get_bank_accounts_search_is_case_insensitive(
        self, test_db, multiple_bank_accounts
    ):
        """Test get_bank_accounts search is case-insensitive"""
        # Act
        result = BankAccountService.get_bank_accounts(
            test_db, page=1, page_size=10, search="bank"
        )

        # Assert - Should find all accounts (all have "Bank" in name)
        assert result.total == 5

    def test_get_bank_accounts_orders_by_created_at_desc(
        self, test_db, multiple_bank_accounts
    ):
        """Test get_bank_accounts returns newest accounts first"""
        # Act
        result = BankAccountService.get_bank_accounts(test_db, page=1, page_size=10)

        # Assert - Newest first
        for i in range(len(result.items) - 1):
            assert result.items[i].created_at >= result.items[i + 1].created_at

    def test_update_bank_account_updates_database(self, test_db, sample_bank_account):
        """Test update_bank_account persists changes to database"""
        # Arrange
        data = BankAccountUpdateRequest(
            bank_name="Updated Bank Name",
            color="#0000FF",
            updated_by="updater@test.com",
        )

        # Act
        result = BankAccountService.update_bank_account(
            test_db, sample_bank_account.id, data
        )

        # Assert
        assert result.bank_name == "Updated Bank Name"
        assert result.color == "#0000FF"
        assert result.updated_by == "updater@test.com"
        assert result.updated_at > sample_bank_account.created_at

        # Verify in database
        db_account = (
            test_db.query(BankAccount)
            .filter(BankAccount.id == sample_bank_account.id)
            .first()
        )
        assert db_account.bank_name == "Updated Bank Name"

    def test_update_bank_account_partial_update_preserves_other_fields(
        self, test_db, sample_bank_account
    ):
        """Test update_bank_account only updates provided fields"""
        # Arrange
        original_bank_name = sample_bank_account.bank_name
        data = BankAccountUpdateRequest(account_number="9999")

        # Act
        result = BankAccountService.update_bank_account(
            test_db, sample_bank_account.id, data
        )

        # Assert
        assert result.account_number == "9999"
        assert result.bank_name == original_bank_name  # Unchanged

    def test_update_bank_account_raises_not_found_for_missing_account(self, test_db):
        """Test update_bank_account raises NotFoundException"""
        # Arrange
        random_id = uuid4()
        data = BankAccountUpdateRequest(bank_name="Updated")

        # Act & Assert
        with pytest.raises(NotFoundException):
            BankAccountService.update_bank_account(test_db, random_id, data)

    def test_delete_bank_account_raises_not_found_for_missing_account(self, test_db):
        """Test delete_bank_account raises NotFoundException"""
        # Arrange
        random_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundException):
            BankAccountService.delete_bank_account(test_db, random_id)

    def test_transaction_rollback_on_error(self, test_db, sample_project):
        """Test database transaction rolls back on error"""
        # Arrange
        initial_count = test_db.query(BankAccount).count()

        # This test verifies that if an error occurs, changes are rolled back
        # We'll create an account but don't commit manually
        account = BankAccount(
            project_id=sample_project.id,
            account_number="9999",
            bank_name="Test",
            account_type="checking",
            created_by="test@test.com",
        )
        test_db.add(account)
        test_db.rollback()  # Manually rollback

        # Assert - No new account
        assert test_db.query(BankAccount).count() == initial_count
