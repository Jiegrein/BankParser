"""
File validation service that orchestrates validation
"""

from fastapi import UploadFile, HTTPException
from typing import BinaryIO
from app.config import get_settings
from .interface import FileValidatorInterface


class FileValidationService:
    """Service for file validation (Dependency Inversion Principle)"""
    
    def __init__(self, validator: FileValidatorInterface):
        self.validator = validator
    
    async def validate_upload(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        # Check if file was uploaded
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Check file type
        if not self.validator.validate_file_type(file):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Only PDF files are allowed."
            )
        
        # Check file size
        if not self.validator.validate_file_size(file):
            settings = get_settings()
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB."
            )
    
    async def validate_content(self, file_content: BinaryIO) -> None:
        """Validate file content"""
        if hasattr(self.validator, 'validate_file_content'):
            if not self.validator.validate_file_content(file_content):
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid PDF file content."
                )