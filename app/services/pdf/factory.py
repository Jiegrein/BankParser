"""
PDF Processor Factory for creating different PDF processing instances
"""

from .interface import PDFProcessorInterface
from .text_extractor import TextExtractor
from .image_extractor import ImageExtractor


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
    
    @staticmethod
    def create_default_processor() -> PDFProcessorInterface:
        """Create default processor (image processor for vision models)"""
        return ImageExtractor()


# Convenience exports
__all__ = [
    'PDFProcessorInterface',
    'PDFProcessorFactory',
    'TextExtractor',
    'ImageExtractor'
]