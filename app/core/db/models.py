"""
SQLAlchemy models for REAMS database
Code-first database models
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, ForeignKey,
    Enum as SQLEnum, Numeric, Date, Time, DECIMAL
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from .base import Base


# Enums
class TransactionType(str, enum.Enum):
    """Transaction type enum"""
    DEBIT = "debit"
    CREDIT = "credit"


# Models
class Project(Base):
    """
    Projects table - Root entity for real estate projects
    """
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    developer_name = Column(String, nullable=False)
    investor_name = Column(String, nullable=False)
    is_activated = Column(Boolean, default=True, nullable=False)
    remarks = Column(Text, nullable=True)

    # Audit fields
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    updated_by = Column(String, nullable=True)

    # Relationships
    bank_accounts = relationship("BankAccount", back_populates="project", cascade="all, delete-orphan")
    category_positions = relationship("ProjectCategoryPosition", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name})>"


class BankAccount(Base):
    """
    Bank accounts table - Belongs to a project
    """
    __tablename__ = "bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    account_number = Column(String, nullable=False)  # Last 4 digits only
    bank_name = Column(String, nullable=False)
    color = Column(String, nullable=True)
    account_type = Column(String, nullable=False)
    position_x = Column(DECIMAL, nullable=True)
    position_y = Column(DECIMAL, nullable=True)

    # Audit fields
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    updated_by = Column(String, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="bank_accounts")
    statement_files = relationship("BankStatementFile", back_populates="bank_account", cascade="all, delete-orphan")
    statement_entries = relationship("BankStatementEntry", back_populates="bank_account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BankAccount(id={self.id}, bank_name={self.bank_name}, account={self.account_number})>"


class Category(Base):
    """
    Categories table - Master data for transaction categorization
    """
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    identification_regex = Column(Text, nullable=True)  # Regex for auto-categorization
    color = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)

    # Audit fields
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    updated_by = Column(String, nullable=True)

    # Relationships
    statement_entries = relationship("BankStatementEntry", back_populates="category")
    entry_splits = relationship("BankStatementEntrySplit", back_populates="category")
    project_positions = relationship("ProjectCategoryPosition", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"


class BankStatementFile(Base):
    """
    Bank statement files table - Uploaded statement files
    """
    __tablename__ = "bank_statement_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False)
    file_path = Column(String, nullable=False)  # Azure Blob Storage URL
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Audit fields
    uploaded_by = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    updated_by = Column(String, nullable=True)

    # Relationships
    bank_account = relationship("BankAccount", back_populates="statement_files")
    entries = relationship("BankStatementEntry", back_populates="statement_file", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BankStatementFile(id={self.id}, period={self.period_start} to {self.period_end})>"


class BankStatementEntry(Base):
    """
    Bank statement entries table - Individual transactions from statements
    """
    __tablename__ = "bank_statement_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_statement_file_id = Column(UUID(as_uuid=True), ForeignKey("bank_statement_files.id"), nullable=False)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)

    tags_csv = Column(JSONB, nullable=True)  # Free-form tags as JSONB
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=True)
    description = Column(Text, nullable=False)
    transaction_reference = Column(String, nullable=True)
    debit_credit = Column(SQLEnum(TransactionType, name="transaction_type"), nullable=False)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    balance = Column(Numeric(precision=15, scale=2), nullable=True)
    notes = Column(Text, nullable=True)

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    modified_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)

    # Relationships
    statement_file = relationship("BankStatementFile", back_populates="entries")
    bank_account = relationship("BankAccount", back_populates="statement_entries")
    category = relationship("Category", back_populates="statement_entries")
    splits = relationship("BankStatementEntrySplit", back_populates="entry", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BankStatementEntry(id={self.id}, date={self.date}, amount={self.amount}, type={self.debit_credit})>"


class BankStatementEntrySplit(Base):
    """
    Bank statement entry splits table - Split transactions across multiple categories
    """
    __tablename__ = "bank_statement_entry_splits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_statement_entry_id = Column(UUID(as_uuid=True), ForeignKey("bank_statement_entries.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)

    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    description = Column(Text, nullable=True)

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    modified_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)

    # Relationships
    entry = relationship("BankStatementEntry", back_populates="splits")
    category = relationship("Category", back_populates="entry_splits")

    def __repr__(self):
        return f"<BankStatementEntrySplit(id={self.id}, amount={self.amount})>"


class ProjectCategoryPosition(Base):
    """
    Project category positions table - Visual positioning of categories per project
    For dashboard visualization (drag-drop categories on 2D canvas)
    """
    __tablename__ = "project_category_positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)

    position_x = Column(DECIMAL, nullable=True)
    position_y = Column(DECIMAL, nullable=True)

    # Audit fields
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    updated_by = Column(String, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="category_positions")
    category = relationship("Category", back_populates="project_positions")

    def __repr__(self):
        return f"<ProjectCategoryPosition(id={self.id}, project_id={self.project_id}, category_id={self.category_id})>"
