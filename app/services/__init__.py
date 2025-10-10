"""
Services package - provides access to all service components

This package follows a modular structure where each service type
has its own sub-package with separated implementations.
"""

# LLM Services
from .llm.interface import LLMServiceInterface
from .llm.factory import LLMServiceFactory
from .llm.openai_service import OpenAIService
from .llm.claude_service import ClaudeService
from .llm.gemini_service import GeminiService

# PDF Services  
from .pdf.interface import PDFProcessorInterface
from .pdf.factory import PDFProcessorFactory
from .pdf.text_extractor import TextExtractor
from .pdf.image_extractor import ImageExtractor

# Validation Services
from .validation.interface import FileValidatorInterface
from .validation.factory import FileValidationFactory
from .validation.pdf_validator import PDFFileValidator
from .validation.validation_service import FileValidationService

# Main Parser Service
from .parser_service import BankStatementParserService, BankStatementParserFactory

__all__ = [
    # LLM Services
    'LLMServiceInterface',
    'LLMServiceFactory', 
    'OpenAIService',
    'ClaudeService',
    'GeminiService',
    
    # PDF Services
    'PDFProcessorInterface',
    'PDFProcessorFactory',
    'TextExtractor',
    'ImageExtractor',
    
    # Validation Services
    'FileValidatorInterface',
    'FileValidationFactory',
    'PDFFileValidator', 
    'FileValidationService',
    
    # Main Parser
    'BankStatementParserService',
    'BankStatementParserFactory'
]