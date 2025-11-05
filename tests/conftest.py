"""
Pytest configuration and shared fixtures
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.db.models import BankAccount, Project, Category, BankStatementFile
from app.core.db.session import get_db
from main import app

# ============================================================================
# Database Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def test_engine():
    """Create in-memory SQLite engine for testing"""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )

    # Only create Project, BankAccount, Category, and BankStatementFile tables for testing (they don't have JSONB)
    # Other tables with PostgreSQL-specific types will be skipped
    Project.__table__.create(engine, checkfirst=True)
    BankAccount.__table__.create(engine, checkfirst=True)
    Category.__table__.create(engine, checkfirst=True)
    BankStatementFile.__table__.create(engine, checkfirst=True)

    yield engine

    BankStatementFile.__table__.drop(engine, checkfirst=True)
    Category.__table__.drop(engine, checkfirst=True)
    BankAccount.__table__.drop(engine, checkfirst=True)
    Project.__table__.drop(engine, checkfirst=True)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine) -> Session:
    """Create test database session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = TestingSessionLocal()
    yield session
    session.close()


# ============================================================================
# API Client Fixture
# ============================================================================


@pytest.fixture(scope="function")
def client(test_db):
    """FastAPI test client with database override"""

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        "name": "Test Project",
        "developer_name": "Test Developer Corp",
        "investor_name": "Test Investor Group",
        "remarks": "Test project remarks",
        "created_by": "test@example.com",
    }


@pytest.fixture
def sample_project(test_db, sample_project_data) -> Project:
    """Create and return a sample project in the database"""
    project = Project(
        name=sample_project_data["name"],
        developer_name=sample_project_data["developer_name"],
        investor_name=sample_project_data["investor_name"],
        remarks=sample_project_data["remarks"],
        created_by=sample_project_data["created_by"],
        is_activated=True,
    )
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)
    return project


@pytest.fixture
def multiple_projects(test_db) -> list[Project]:
    """Create multiple projects for pagination testing"""
    projects = []
    for i in range(5):
        project = Project(
            name=f"Project {i + 1}",
            developer_name=f"Developer {i + 1}",
            investor_name=f"Investor {i + 1}",
            remarks=f"Remarks {i + 1}",
            created_by=f"user{i + 1}@example.com",
            is_activated=True if i % 2 == 0 else False,  # Alternate active/inactive
        )
        test_db.add(project)
        projects.append(project)

    test_db.commit()
    for project in projects:
        test_db.refresh(project)

    return projects


# ============================================================================
# Bank Account Fixtures
# ============================================================================


@pytest.fixture
def sample_bank_account_data(sample_project):
    """Sample bank account data for testing"""
    return {
        "project_id": sample_project.id,
        "account_number": "1234",
        "bank_name": "Test Bank",
        "account_type": "checking",
        "color": "#FF5733",
        "created_by": "test@example.com",
    }


@pytest.fixture
def sample_bank_account(test_db, sample_project) -> BankAccount:
    """Create and return a sample bank account in the database"""
    account = BankAccount(
        project_id=sample_project.id,
        account_number="1234",
        bank_name="Test Bank",
        account_type="checking",
        color="#FF5733",
        created_by="test@example.com",
    )
    test_db.add(account)
    test_db.commit()
    test_db.refresh(account)
    return account


@pytest.fixture
def multiple_bank_accounts(test_db, sample_project) -> list[BankAccount]:
    """Create multiple bank accounts for pagination testing"""
    accounts = []
    for i in range(5):
        account = BankAccount(
            project_id=sample_project.id,
            account_number=f"123{i}",
            bank_name=f"Bank {i + 1}",
            account_type="checking" if i % 2 == 0 else "savings",
            color=f"#FF{i}{i}{i}{i}",
            created_by=f"user{i + 1}@example.com",
        )
        test_db.add(account)
        accounts.append(account)

    test_db.commit()
    for account in accounts:
        test_db.refresh(account)

    return accounts


# ============================================================================
# Category Fixtures
# ============================================================================


@pytest.fixture
def sample_category_data():
    """Sample category data for testing"""
    return {
        "name": "Test Category",
        "identification_regex": ".*TEST.*",
        "color": "#4CAF50",
        "description": "Test category description",
        "created_by": "test@example.com",
    }


@pytest.fixture
def sample_category(test_db) -> Category:
    """Create and return a sample category in the database"""
    category = Category(
        name="Test Category",
        identification_regex=".*TEST.*",
        color="#4CAF50",
        description="Test category description",
        is_active=True,
        created_by="test@example.com",
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


@pytest.fixture
def multiple_categories(test_db) -> list[Category]:
    """Create multiple categories for pagination testing"""
    categories = []
    for i in range(5):
        category = Category(
            name=f"Category {i + 1}",
            identification_regex=f".*CAT{i}.*",
            color=f"#FF{i}{i}{i}{i}",
            description=f"Category {i + 1} description",
            is_active=True if i % 2 == 0 else False,  # Alternate active/inactive
            created_by=f"user{i + 1}@example.com",
        )
        test_db.add(category)
        categories.append(category)

    test_db.commit()
    for category in categories:
        test_db.refresh(category)

    return categories


@pytest.fixture
def random_uuid():
    """Generate random UUID for testing"""
    return uuid4()


# ============================================================================
# Bank Statement File Fixtures
# ============================================================================


@pytest.fixture
def sample_statement_file_data(sample_bank_account):
    """Sample bank statement file data for testing"""
    from datetime import date
    return {
        "bank_account_id": sample_bank_account.id,
        "file_path": "https://storage.blob.core.windows.net/statements/test_statement.pdf",
        "period_start": date(2024, 1, 1),
        "period_end": date(2024, 1, 31),
        "uploaded_by": "test@example.com",
    }


@pytest.fixture
def sample_statement_file(test_db, sample_bank_account) -> BankStatementFile:
    """Create and return a sample bank statement file in the database"""
    from datetime import date
    statement_file = BankStatementFile(
        bank_account_id=sample_bank_account.id,
        file_path="https://storage.blob.core.windows.net/statements/test_statement.pdf",
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        uploaded_by="test@example.com",
    )
    test_db.add(statement_file)
    test_db.commit()
    test_db.refresh(statement_file)
    return statement_file


@pytest.fixture
def multiple_statement_files(test_db, sample_bank_account) -> list[BankStatementFile]:
    """Create multiple statement files for pagination testing"""
    from datetime import date
    statement_files = []
    for i in range(5):
        statement_file = BankStatementFile(
            bank_account_id=sample_bank_account.id,
            file_path=f"https://storage.blob.core.windows.net/statements/statement_{i}.pdf",
            period_start=date(2024, i + 1, 1),
            period_end=date(2024, i + 1, 28),
            uploaded_by=f"user{i + 1}@example.com",
        )
        test_db.add(statement_file)
        statement_files.append(statement_file)

    test_db.commit()
    for statement_file in statement_files:
        test_db.refresh(statement_file)

    return statement_files
