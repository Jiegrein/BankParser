from abc import ABC, abstractmethod
from typing import BinaryIO, List
import base64
from io import BytesIO
from PIL import Image
import pdf2image
import PyPDF2
import pdfplumber
from app.models import BankStatement


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
        raise NotImplementedError("Text extractor doesn't support image conversion")


class ImageExtractor(PDFProcessorInterface):
    """Image extraction implementation using pdf2image"""
    
    async def extract_text(self, file_content: BinaryIO) -> str:
        """Not implemented for image extractor"""
        raise NotImplementedError("Image extractor doesn't support text extraction")
    
    async def convert_to_images(self, file_content: BinaryIO) -> List[str]:
        """Convert PDF pages to base64 encoded images"""
        try:
            # Reset file pointer
            file_content.seek(0)
            
            # Convert PDF to images
            images = pdf2image.convert_from_bytes(file_content.read())
            
            base64_images = []
            for image in images:
                # Convert PIL Image to base64
                buffer = BytesIO()
                image.save(buffer, format='PNG')
                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                base64_images.append(img_base64)
            
            return base64_images
        except Exception as e:
            raise Exception(f"Failed to convert PDF to images: {str(e)}")


class PDFProcessorFactory:
    """Factory for creating PDF processors (Factory Pattern)"""
    
    @staticmethod
    def create_text_processor() -> PDFProcessorInterface:
        """Create text processor"""
        return TextExtractor()
    
    @staticmethod
    def create_image_processor() -> PDFProcessorInterface:
        """Create image processor"""
        return ImageExtractor()