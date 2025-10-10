"""
Text extraction implementation using pdfplumber
"""

from typing import BinaryIO, List
import pdfplumber
from .interface import PDFProcessorInterface


class TextExtractor(PDFProcessorInterface):
    """Text extraction implementation using pdfplumber"""
    
    async def extract_text(self, file_content: BinaryIO) -> str:
        """Extract text from PDF using pdfplumber"""
        try:
            text_content = ""
            with pdfplumber.open(file_content) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            return text_content
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    async def convert_to_images(self, file_content: BinaryIO) -> List[str]:
        """Not implemented for text extractor"""
        raise NotImplementedError(
            "Text extractor doesn't support image conversion. "
            "Use ImageExtractor for image conversion."
        )