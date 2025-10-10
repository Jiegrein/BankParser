from fastapi import UploadFile, HTTPException
from typing import BinaryIO
import magic
from app.config import get_settings


class FileValidatorInterface:
    """Interface for file validation (Interface Segregation Principle)"""
    
    def validate_file_type(self, file: UploadFile) -> bool:
        """Validate file type"""
        pass
    
    def validate_file_size(self, file: UploadFile) -> bool:
        """Validate file size"""
        pass


class PDFFileValidator(FileValidatorInterface):
    """PDF file validator implementation (Single Responsibility Principle)"""
    
    def __init__(self):
        self.settings = get_settings()
    
    def validate_file_type(self, file: UploadFile) -> bool:
        """Validate that the file is a PDF"""
        try:
            # Check file extension
            if not file.filename.lower().endswith('.pdf'):
                return False
            
            # Check MIME type
            if file.content_type not in ['application/pdf']:
                return False
            
            return True
            
        except Exception:
            return False
    
    def validate_file_size(self, file: UploadFile) -> bool:
        """Validate file size"""
        try:
            # Check if file size is within limits
            max_size_bytes = self.settings.max_file_size_mb * 1024 * 1024
            
            # Get file size by reading content length
            if hasattr(file, 'size') and file.size:
                return file.size <= max_size_bytes
            
            # If size not available, we'll check during processing
            return True
            
        except Exception:
            return False
    
    def validate_file_content(self, file_content: BinaryIO) -> bool:
        """Validate file content using magic numbers"""
        try:
            # Reset file pointer
            file_content.seek(0)
            
            # Read first few bytes to check PDF magic number
            header = file_content.read(10)
            file_content.seek(0)
            
            # PDF files start with %PDF
            return header.startswith(b'%PDF')
            
        except Exception:
            return False


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