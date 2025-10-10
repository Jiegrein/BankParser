from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel


class Transaction(BaseModel):
    """Transaction data model"""
    date: str
    description: str
    amount: float
    type: str  # "credit" or "debit"
    category: Optional[str] = None
    balance: Optional[float] = None


class BankStatement(BaseModel):
    """Bank statement data model"""
    account_holder: str
    bank_name: str
    account_number: str
    statement_period: Dict[str, str]  # start_date, end_date
    opening_balance: float
    closing_balance: float
    transactions: List[Transaction]
    currency: str = "USD"
    
    
class ParsedResponse(BaseModel):
    """API response model"""
    success: bool
    data: Optional[BankStatement] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None


class FileUploadRequest(BaseModel):
    """File upload validation model"""
    filename: str
    content_type: str
    size: int