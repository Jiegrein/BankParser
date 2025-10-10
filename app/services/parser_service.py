from typing import BinaryIO
import time
from io import BytesIO
from fastapi import UploadFile

from app.models import BankStatement, ParsedResponse
from app.services.pdf_processor import PDFProcessorFactory, PDFProcessorInterface
from app.services.llm_service import LLMServiceFactory, LLMServiceInterface
from app.services.file_validator import FileValidationService, PDFFileValidator


class BankStatementParserService:
    """
    Main service for parsing bank statements (Single Responsibility Principle)
    Orchestrates the entire parsing workflow
    """
    
    def __init__(
        self,
        pdf_processor: PDFProcessorInterface = None,
        llm_service: LLMServiceInterface = None,
        file_validator: FileValidationService = None
    ):
        # Dependency Injection (Dependency Inversion Principle)
        self.pdf_processor = pdf_processor or PDFProcessorFactory.create_image_processor()
        self.llm_service = llm_service or LLMServiceFactory.create_openai_service()
        self.file_validator = file_validator or FileValidationService(PDFFileValidator())
    
    async def parse_statement(self, file: UploadFile, use_vision: bool = True) -> ParsedResponse:
        """
        Parse bank statement from uploaded PDF file
        
        Args:
            file: Uploaded PDF file
            use_vision: Whether to use vision model (True) or text extraction (False)
        
        Returns:
            ParsedResponse with parsed bank statement data
        """
        start_time = time.time()
        
        try:
            # Step 1: Validate file
            await self.file_validator.validate_upload(file)
            
            # Step 2: Read file content
            file_content = BytesIO(await file.read())
            await self.file_validator.validate_content(file_content)
            
            # Step 3: Process PDF based on method
            if use_vision:
                bank_statement = await self._parse_with_vision(file_content)
            else:
                bank_statement = await self._parse_with_text(file_content)
            
            processing_time = time.time() - start_time
            
            return ParsedResponse(
                success=True,
                data=bank_statement,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ParsedResponse(
                success=False,
                error=str(e),
                processing_time=processing_time
            )
    
    async def _parse_with_vision(self, file_content: BinaryIO) -> BankStatement:
        """Parse using vision model"""
        # Convert PDF to images
        base64_images = await self.pdf_processor.convert_to_images(file_content)
        
        # Parse with LLM vision
        return await self.llm_service.parse_image_statement(base64_images)
    
    async def _parse_with_text(self, file_content: BinaryIO) -> BankStatement:
        """Parse using text extraction"""
        # Use text processor
        text_processor = PDFProcessorFactory.create_text_processor()
        
        # Extract text from PDF
        text_content = await text_processor.extract_text(file_content)
        
        # Parse with LLM text
        return await self.llm_service.parse_text_statement(text_content)


class BankStatementParserFactory:
    """Factory for creating parser service instances (Factory Pattern)"""
    
    @staticmethod
    def create_vision_parser() -> BankStatementParserService:
        """Create parser with vision capabilities (OpenAI)"""
        return BankStatementParserService(
            pdf_processor=PDFProcessorFactory.create_image_processor(),
            llm_service=LLMServiceFactory.create_openai_service()
        )
    
    @staticmethod
    def create_text_parser() -> BankStatementParserService:
        """Create parser with text extraction capabilities (OpenAI)"""
        return BankStatementParserService(
            pdf_processor=PDFProcessorFactory.create_text_processor(),
            llm_service=LLMServiceFactory.create_openai_service()
        )
    
    @staticmethod
    def create_claude_parser() -> BankStatementParserService:
        """Create parser with Claude LLM"""
        return BankStatementParserService(
            pdf_processor=PDFProcessorFactory.create_image_processor(),
            llm_service=LLMServiceFactory.create_claude_service()
        )
    
    @staticmethod
    def create_gemini_parser() -> BankStatementParserService:
        """Create parser with Gemini LLM"""
        return BankStatementParserService(
            pdf_processor=PDFProcessorFactory.create_image_processor(),
            llm_service=LLMServiceFactory.create_gemini_service()
        )
    
    @staticmethod
    def create_custom_parser(
        pdf_processor: PDFProcessorInterface,
        llm_service: LLMServiceInterface
    ) -> BankStatementParserService:
        """Create parser with custom components"""
        return BankStatementParserService(
            pdf_processor=pdf_processor,
            llm_service=llm_service
        )
    
    @staticmethod
    def create_default_parser() -> BankStatementParserService:
        """Create parser with default configuration (OpenAI vision-enabled)"""
        return BankStatementParserService()