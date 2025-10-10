from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
import logging
from enum import Enum

from app.models import ParsedResponse
from app.services.parser_service import BankStatementParserFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["Bank Statement Parser"])


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    openai = "openai"
    claude = "claude"
    gemini = "gemini"


def get_parser_service(llm_provider: LLMProvider, use_vision: bool = True):
    """Get parser service based on LLM provider"""
    if llm_provider == LLMProvider.openai:
        return BankStatementParserFactory.create_openai_vision_parser() if use_vision else BankStatementParserFactory.create_openai_text_parser()
    elif llm_provider == LLMProvider.claude:
        return BankStatementParserFactory.create_claude_parser()
    elif llm_provider == LLMProvider.gemini:
        return BankStatementParserFactory.create_gemini_parser()
    else:
        return BankStatementParserFactory.create_default_parser()


@router.post(
    "/parse-statement",
    response_model=ParsedResponse,
    summary="Parse Bank Statement",
    description="Upload a PDF bank statement and get standardized JSON output"
)
async def parse_bank_statement(
    file: UploadFile = File(..., description="Bank statement PDF file"),
    use_vision: bool = Query(
        default=True, 
        description="Use vision model (True) or text extraction (False)"
    ),
    llm_provider: LLMProvider = Query(
        default=LLMProvider.openai,
        description="Choose which LLM provider to use"
    )
) -> JSONResponse:
    """
    Parse bank statement from uploaded PDF file
    
    - **file**: PDF file containing the bank statement
    - **use_vision**: Whether to use vision model (recommended) or text extraction
    - **llm_provider**: Which LLM provider to use (openai, claude, gemini)
    
    Returns standardized bank statement data in JSON format
    """
    
    try:
        logger.info(f"Processing file: {file.filename}, use_vision: {use_vision}, llm_provider: {llm_provider}")
        
        # Get appropriate parser service
        parser_service = get_parser_service(llm_provider, use_vision)
        
        # Parse the statement
        result = await parser_service.parse_statement(file, use_vision)
        
        # Log processing result
        if result.success:
            logger.info(f"Successfully parsed statement with {llm_provider} in {result.processing_time:.2f}s")
            return JSONResponse(
                status_code=200,
                content=result.dict()
            )
        else:
            logger.error(f"Failed to parse statement with {llm_provider}: {result.error}")
            return JSONResponse(
                status_code=422,
                content=result.dict()
            )
            
    except Exception as e:
        logger.error(f"Unexpected error with {llm_provider}: {str(e)}")
        error_response = ParsedResponse(
            success=False,
            error=f"Unexpected error with {llm_provider}: {str(e)}"
        )
        return JSONResponse(
            status_code=500,
            content=error_response.dict()
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the API is running"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Bank Statement Parser API",
        "version": "1.0.0"
    }


@router.get(
    "/supported-formats",
    summary="Supported File Formats",
    description="Get list of supported file formats and LLM providers"
)
async def get_supported_formats():
    """Get supported file formats and LLM providers"""
    return {
        "supported_formats": ["PDF"],
        "max_file_size_mb": 10,
        "llm_providers": {
            "openai": {
                "name": "OpenAI GPT-4",
                "vision_support": True,
                "text_support": True,
                "status": "active"
            },
            "claude": {
                "name": "Anthropic Claude",
                "vision_support": True,
                "text_support": True,
                "status": "pending_implementation"
            },
            "gemini": {
                "name": "Google Gemini",
                "vision_support": True,
                "text_support": True,
                "status": "pending_implementation"
            }
        },
        "features": [
            "Vision-based parsing",
            "Text extraction parsing",
            "Standardized JSON output",
            "Multiple bank support",
            "Multiple LLM providers"
        ]
    }