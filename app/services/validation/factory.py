"""
File Validation Factory for creating different validation instances
"""

from .interface import FileValidatorInterface
from .pdf_validator import PDFFileValidator
from .validation_service import FileValidationService


class FileValidationFactory:
    """Factory for creating file validators (Factory Pattern)"""
    
    @staticmethod
    def create_pdf_validator() -> FileValidatorInterface:
        """Create PDF file validator"""
        return PDFFileValidator()
    
    @staticmethod
    def create_pdf_validation_service() -> FileValidationService:
        """Create PDF validation service"""
        return FileValidationService(PDFFileValidator())
    
    @staticmethod
    def create_default_validation_service() -> FileValidationService:
        """Create default validation service (PDF)"""
        return FileValidationService(PDFFileValidator())


# Convenience exports
__all__ = [
    'FileValidatorInterface',
    'FileValidationFactory',
    'PDFFileValidator',
    'FileValidationService'
]