"""
Image extraction implementation using pdf2image
"""

from typing import BinaryIO, List
import base64
from io import BytesIO
from PIL import Image
import pdf2image
from .interface import PDFProcessorInterface


class ImageExtractor(PDFProcessorInterface):
    """Image extraction implementation using pdf2image"""
    
    async def extract_text(self, file_content: BinaryIO) -> str:
        """Not implemented for image extractor"""
        raise NotImplementedError(
            "Image extractor doesn't support text extraction. "
            "Use TextExtractor for text extraction."
        )
    
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