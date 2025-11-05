# Exception Handling

Global exception handling system for consistent error responses across the API.

## Overview

This module provides structured exception handling with:
- Custom exception classes
- Global exception handlers
- Consistent error responses
- Debug vs production modes

## Quick Start

### 1. Using Custom Exceptions

```python
from app.core.exceptions import NotFoundException, BadRequestException

# In your service/route
def get_project(db: Session, project_id: str):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException(
            message=f"Project with ID {project_id} not found",
            details={"project_id": project_id}
        )
    return project
```

### 2. Exception Types

| Exception | Status Code | Use Case |
|-----------|-------------|----------|
| `NotFoundException` | 404 | Resource not found |
| `BadRequestException` | 400 | Invalid request data |
| `UnauthorizedException` | 401 | Not authenticated |
| `ForbiddenException` | 403 | Not authorized |
| `ConflictException` | 409 | Resource already exists |
| `ValidationException` | 422 | Business logic validation failed |
| `AppException` | Custom | Base exception for custom errors |

## Registration

Exception handlers are registered in `main.py`:

```python
from app.core.exceptions import register_exception_handlers

register_exception_handlers(app)
# All exception handling now automatic!
```

## Examples

### Basic Usage

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter()

@router.get("/projects/{project_id}")
async def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise NotFoundException(
            message=f"Project with ID {project_id} not found",
            details={"project_id": project_id}
        )

    return project
```

### Custom Exception

```python
from app.core.exceptions import AppException

class ProjectAlreadyExistsException(AppException):
    def __init__(self, project_name: str):
        super().__init__(
            message=f"Project '{project_name}' already exists",
            status_code=409,
            error_code="PROJECT_EXISTS",
            details={"project_name": project_name}
        )

# Usage
if existing_project:
    raise ProjectAlreadyExistsException(data.name)
```

### Validation Exception

```python
from app.core.exceptions import ValidationException

def validate_project(data):
    errors = []

    if len(data.name) < 3:
        errors.append("Name must be at least 3 characters")

    if not data.developer_name:
        errors.append("Developer name is required")

    if errors:
        raise ValidationException(
            message="Project validation failed",
            details={"errors": errors}
        )
```

## Error Response Format

All exceptions return a consistent JSON structure:

```json
{
  "success": false,
  "error": "Project with ID 123 not found",
  "error_code": "NOT_FOUND",
  "details": {
    "project_id": "123"
  },
  "path": "/api/v1/projects/123"
}
```

### Debug Mode (DEBUG=True)

Additional information is included:

```json
{
  "success": false,
  "error": "Database constraint violation",
  "error_code": "DATABASE_ERROR",
  "details": {
    "db_error": "UNIQUE constraint failed: projects.name",
    "exception_type": "IntegrityError",
    "traceback": "..."
  },
  "path": "/api/v1/projects"
}
```

## Handlers

### 1. AppException Handler
Handles all custom application exceptions.

```python
raise NotFoundException("Resource not found")
# → 404 with structured error response
```

### 2. RequestValidationError Handler
Handles Pydantic validation errors for request body and query parameters.

```python
# Bad request body
POST /projects
{
  "name": ""  # Too short
}

# Response
{
  "success": false,
  "error": "Validation failed",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "errors": [
      {
        "field": "name",
        "message": "String should have at least 1 characters",
        "type": "string_too_short"
      }
    ]
  }
}
```

### 3. IntegrityError Handler
Handles database constraint violations (unique constraints, foreign keys).

```python
# Duplicate project name
# → 409 Conflict with user-friendly message
```

### 4. SQLAlchemyError Handler
Handles general database errors.

```python
# Database connection lost
# → 500 with database error details (debug mode only)
```

### 5. General Exception Handler
Catch-all for unexpected exceptions.

```python
# Any unhandled exception
# → 500 with full stack trace (debug mode only)
```

## Best Practices

### DO ✅

```python
# Use specific exceptions
raise NotFoundException(f"Project {id} not found")

# Include helpful details
raise BadRequestException(
    message="Invalid project data",
    details={"field": "name", "issue": "too short"}
)

# Use validation exception for business logic
if project.budget < 0:
    raise ValidationException("Budget cannot be negative")
```

### DON'T ❌

```python
# Don't use generic exceptions
raise Exception("Something went wrong")  # ❌

# Don't expose internal details in production
raise AppException(
    message=str(db_error),  # ❌ Might expose sensitive info
    details={"password": "..."}  # ❌ Never expose credentials
)

# Don't ignore exception handling
try:
    risky_operation()
except:
    pass  # ❌ Silent failures are bad
```

## Testing Exceptions

```python
import pytest
from app.core.exceptions import NotFoundException

def test_get_project_not_found():
    with pytest.raises(NotFoundException) as exc_info:
        service.get_project(db, "invalid-id")

    assert exc_info.value.status_code == 404
    assert "not found" in str(exc_info.value)
```

## Logging

All exceptions are automatically logged with appropriate severity:

- **Custom exceptions (AppException)**: `WARNING` level
- **Validation errors**: `WARNING` level
- **Database errors**: `ERROR` level
- **Unhandled exceptions**: `ERROR` level with full stack trace

Logs include:
- Request path
- HTTP method
- Error details
- Stack trace (debug mode)

## Configuration

Exception behavior is controlled by `settings.debug`:

```python
# .env
DEBUG=False  # Production mode
```

**Debug Mode (DEBUG=True):**
- Full stack traces in responses
- Database error details exposed
- Detailed exception information

**Production Mode (DEBUG=False):**
- Generic error messages
- No stack traces
- Minimal information exposure

## File Structure

```
app/core/exceptions/
├── __init__.py      # Public API
├── base.py          # Custom exception classes
├── handlers.py      # Exception handlers
└── README.md        # This file
```

## Adding New Exceptions

1. **Create exception class** in `base.py`:

```python
class MyCustomException(AppException):
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=418,  # I'm a teapot
            error_code="CUSTOM_ERROR",
            details=details
        )
```

2. **Export** in `__init__.py`:

```python
from .base import MyCustomException

__all__ = [..., "MyCustomException"]
```

3. **Use it**:

```python
from app.core.exceptions import MyCustomException

raise MyCustomException("Something custom happened")
```

## Migration from Old Code

**Before:**
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )
```

**After:**
```python
from app.core.exceptions import register_exception_handlers

register_exception_handlers(app)
# All exception handling now automatic!
```

---

**Questions?** Check main.py to see how handlers are registered.
