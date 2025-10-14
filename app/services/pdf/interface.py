from abc import ABC, abstractmethod
from typing import BinaryIO, List


class PDFProcessorInterface(ABC):
    """Interface for PDF processing (Interface Segregation Principle)"""

    @abstractmethod
    async def extract_text(self, file_content: BinaryIO) -> str:
        """Extract text from PDF"""
        pass

    @abstractmethod
    async def convert_to_images(self, file_content: BinaryIO) -> List[str]:
        """Convert PDF pages to base64 encoded images"""
        pass
