#!/usr/bin/env python3
"""
Bank Statement Parser API

A FastAPI application for parsing bank statements from PDF files
using OpenAI's GPT models and converting them to standardized JSON format.
"""

import uvicorn
from app.config import get_settings

def main():
    """Run the FastAPI application"""
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )

if __name__ == "__main__":
    main()