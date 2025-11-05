"""
PDF file validator implementation
"""

from typing import BinaryIO

from fastapi import UploadFile

from app.config import get_settings

from .interface import FileValidatorInterface


class PDFFileValidator(FileValidatorInterface):
    """PDF file validator implementation (Single Responsibility Principle)"""

    def __init__(self):
        self.settings = get_settings()

    def validate_file_type(self, file: UploadFile) -> bool:
        """Validate that the file is a PDF"""
        try:
            # Check file extension
            if not file.filename.lower().endswith(".pdf"):
                return False

            # Check MIME type
            if file.content_type not in ["application/pdf"]:
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
            if hasattr(file, "size") and file.size:
                return file.size <= max_size_bytes

            # If size not available, we'll check during processing
            return True

        except Exception:
            return False

    def validate_file_content(self, file_content: BinaryIO) -> bool:
        """Validate file content using PDF magic number"""
        try:
            # Reset file pointer
            file_content.seek(0)

            # Read first few bytes to check PDF magic number
            header = file_content.read(10)
            file_content.seek(0)

            # PDF files start with %PDF
            return header.startswith(b"%PDF")

        except Exception:
            return False
