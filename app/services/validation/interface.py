from abc import ABC, abstractmethod
from fastapi import UploadFile
from typing import BinaryIO


class FileValidatorInterface(ABC):
    """Interface for file validation (Interface Segregation Principle)"""
    
    @abstractmethod
    def validate_file_type(self, file: UploadFile) -> bool:
        """Validate file type"""
        pass
    
    @abstractmethod
    def validate_file_size(self, file: UploadFile) -> bool:
        """Validate file size"""
        pass