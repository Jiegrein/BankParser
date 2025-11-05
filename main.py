from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys

from app.config import get_settings
from app.api.routes import router
from app.core.exceptions import register_exception_handlers
from app.features.projects.routes import router as projects_router
from app.features.accounts.routes import router as accounts_router
from app.features.categories.routes import router as categories_router
from app.features.statement_files.routes import router as statement_files_router
from app.features.statement_entries.routes import router as statement_entries_router
from app.features.entry_splits.routes import router as entry_splits_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    🏦 **Bank Statement Parser API**
    
    A powerful API for parsing bank statements from various banks into standardized JSON format.
    
    ## Features
    
    * 📄 **PDF Processing**: Upload PDF bank statements
    * 🤖 **AI-Powered**: Uses GPT-4 Vision for accurate parsing
    * 🏛️ **Multi-Bank Support**: Works with statements from different banks
    * 📊 **Standardized Output**: Consistent JSON format regardless of source bank
    * ⚡ **Fast Processing**: Quick turnaround time
    * 🔒 **Secure**: File validation and error handling
    
    ## Usage
    
    1. Upload a PDF bank statement using the `/api/v1/parse-statement` endpoint
    2. Choose between vision-based or text extraction parsing
    3. Receive standardized JSON with account info, transactions, and balances
    
    ## Supported Banks
    
    Works with statements from major banks including:
    - Chase, Bank of America, Wells Fargo
    - Citibank, Capital One, US Bank
    - And many more...
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure according to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)
app.include_router(projects_router)
app.include_router(accounts_router)
app.include_router(categories_router)
app.include_router(statement_files_router)
app.include_router(statement_entries_router)
app.include_router(entry_splits_router)

# Register global exception handlers
register_exception_handlers(app)

# Root endpoint
@app.get("/", summary="API Root", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health",
        "parse_endpoint": "/api/v1/parse-statement"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Running on {settings.host}:{settings.port}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"Shutting down {settings.app_name}")

if __name__ == "__main__":
    import uvicorn
    
    # Get host and port from environment or settings
    import os
    host = os.getenv("HOST", settings.host)
    port = int(os.getenv("PORT", settings.port))
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=settings.debug,
        log_level="info"
    )