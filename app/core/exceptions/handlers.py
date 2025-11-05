"""
Global exception handlers for consistent error responses
"""

import logging
import traceback

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.config import get_settings

from .base import AppException

logger = logging.getLogger(__name__)
settings = get_settings()


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers to the FastAPI app
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """
        Handle custom application exceptions
        """
        logger.warning(
            f"AppException: {exc.error_code} - {exc.message}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code,
                "error_code": exc.error_code,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.message,
                "error_code": exc.error_code,
                "details": exc.details,
                "path": request.url.path,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors (request body/query params)
        """
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        logger.warning(
            f"Validation error: {len(errors)} error(s)",
            extra={
                "path": request.url.path,
                "method": request.method,
                "errors": errors,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "details": {"errors": errors},
                "path": request.url.path,
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        """
        Handle database integrity errors (unique constraints, foreign keys)
        """
        logger.error(
            f"Database integrity error: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
            },
        )

        # Extract useful error message
        error_message = "Database constraint violation"
        if "unique constraint" in str(exc).lower():
            error_message = "Resource already exists"
        elif "foreign key constraint" in str(exc).lower():
            error_message = "Related resource not found"

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "success": False,
                "error": error_message,
                "error_code": "DATABASE_CONSTRAINT_VIOLATION",
                "details": {
                    "db_error": str(exc.orig) if hasattr(exc, "orig") else str(exc)
                }
                if settings.debug
                else {},
                "path": request.url.path,
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        """
        Handle general SQLAlchemy errors
        """
        logger.error(
            f"Database error: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "exception": str(exc),
            },
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Database error occurred",
                "error_code": "DATABASE_ERROR",
                "details": {"db_error": str(exc)} if settings.debug else {},
                "path": request.url.path,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Catch-all handler for any unhandled exceptions
        """
        # Log full stack trace for debugging
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc() if settings.debug else None,
            },
            exc_info=True,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "An unexpected error occurred"
                if not settings.debug
                else str(exc),
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": {
                    "exception_type": type(exc).__name__,
                    "traceback": traceback.format_exc(),
                }
                if settings.debug
                else {},
                "path": request.url.path,
            },
        )
