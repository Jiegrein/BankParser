# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 IMPORTANT: Coding Workflow Rule

**NEVER write code when the user is asking questions or seeking explanations.**

### The Rule:

1. **When user asks a question** (e.g., "explain X", "how does Y work", "what is Z"):
   - ✅ Provide explanation
   - ✅ Update this CLAUDE.md with the explanation
   - ✅ Ask: "Would you like me to start implementing this?" or "Ready to code this?"
   - ❌ DO NOT write code immediately

2. **When user explicitly requests coding** (e.g., "start", "go", "do it", "implement this"):
   - ✅ Write the code
   - ✅ Use the TodoWrite tool to track progress
   - ✅ Provide clear commit-ready implementation

3. **When user wants to review first**:
   - ✅ Show file structure/pseudocode
   - ✅ Explain approach
   - ✅ Wait for confirmation before coding

### Examples:

**❌ WRONG:**

```
User: "explain how exception handling works"
Claude: [creates exception handler files immediately]
```

**✅ CORRECT:**

```
User: "explain how exception handling works"
Claude: [explains and updates CLAUDE.md]
        "I've documented this in CLAUDE.md. Would you like me to implement the exception handlers now?"
User: "yes, go"
Claude: [now writes the code]
```

### Why This Rule Exists:

- Prevents premature implementation
- Allows user to review approach first
- Keeps documentation updated
- Gives user control over when code is written
- Separates learning/planning from implementation

**Always ask before coding. Only code when user explicitly says to proceed.**

---

## Project Overview

Bank Statement Parser is a FastAPI application that extracts structured data from bank statement PDFs using LLM providers (OpenAI GPT-4, Claude, Gemini). The architecture follows SOLID principles with heavy use of dependency injection, factory patterns, and interface segregation.

## Common Commands

### Running the Application

```bash
# Standard way
python main.py

# Or using uvicorn directly
uvicorn main:app --reload

# Access API docs
# http://localhost:8000/docs
```

### Docker

```bash
# Production - Build and run (port 8000)
docker-compose up --build

# Development - Build and run with dev profile (port 8001 + PostgreSQL)
docker-compose --profile dev up --build

# Build only
docker build -t bank-parser .

# Run container manually
docker run -p 8000:8000 --env-file .env bank-parser
```

**Docker Profiles:**

- **Default (no profile)**: Runs `bankparser` service on port 8000 (production mode)
- **`--profile dev`**: Runs `bankparser-dev` service on port 8001 + `postgres` database on port 5432
- **`--profile production`**: Includes `nginx` reverse proxy on ports 80/443

### Development & Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests (if tests exist)
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Format code
black .
isort .

# Lint
flake8 app/
mypy app/
```

### Testing the API

```bash
# Parse a statement with OpenAI
curl -X POST "http://localhost:8000/api/v1/parse-statement?use_vision=true&llm_provider=openai" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@statement.pdf"

# Health check
curl http://localhost:8000/api/v1/health
```

## Architecture Overview

### Core Design Patterns

The codebase is built around three main architectural concepts:

1. **Interface Segregation + Dependency Inversion**: All major components (PDF processors, LLM services, validators) implement clean interfaces and are injected as dependencies.

2. **Factory Pattern**: Factories (`LLMServiceFactory`, `PDFProcessorFactory`, `BankStatementParserFactory`) create pre-configured service combinations.

3. **Strategy Pattern**: Different LLM providers and PDF processing strategies can be swapped at runtime without changing core logic.

### Key Abstraction Layers

```
API Layer (routes.py)
    ↓
Parser Service (parser_service.py) - orchestrates the workflow
    ↓
├── PDF Processor Interface → Image or Text Extraction
├── LLM Service Interface → OpenAI, Claude, or Gemini
└── Validation Service → File validation
```

### LLM Service Architecture

All LLM services inherit from `BaseLLMService` (in `app/services/llm/base.py`), which provides:

- **Shared parsing prompt** via `_get_parsing_prompt()`
- **Robust JSON parsing** with multiple fallback strategies to handle:
  - Markdown code fences
  - Trailing commas
  - Thousands separators in numbers
  - Mixed response formats
- **Pagination support** for multi-page statements via `has_more` and `next_page_hint` fields
- **Image deduplication** using SHA-1 hashing

Concrete implementations (OpenAIService, ClaudeService, GeminiService) only need to implement:

- `_single_text_call()` - single text-based LLM call
- `_single_image_call()` - single vision-based LLM call

The base class handles pagination, merging, and conversion to `BankStatement` models.

### Adding New LLM Providers

See `ADDING_NEW_LLMS.md` for detailed guide. Summary:

1. Create class extending `BaseLLMService` in `app/services/llm/`
2. Implement `_single_text_call()` and `_single_image_call()` methods
3. Add factory method to `LLMServiceFactory`
4. Add factory method to `BankStatementParserFactory`
5. Optionally update `LLMProvider` enum in `app/api/routes.py`

Example: `app/services/llm/openai_service.py` shows the full implementation pattern.

### PDF Processing

Two strategies available:

- **ImagePDFProcessor** (`app/services/pdf/image_extractor.py`): Converts PDF pages to base64 images for vision models
- **TextPDFProcessor** (`app/services/pdf/text_extractor.py`): Extracts raw text from PDFs for text-only models

Both implement `PDFProcessorInterface`.

### Data Models

All models use Pydantic (in `app/models.py`):

- `Transaction`: Individual transaction with date, description, amount, type, category
- `BankStatement`: Complete statement with holder, bank, period, balances, transactions
- `ParsedResponse`: API response wrapper with success flag, data, error, processing_time

## Configuration

Environment variables (`.env` file):

```
# LLM API Keys
OPENAI_API_KEY=your_key_here
CLAUDE_API_KEY=your_key_here  # if using Claude
GEMINI_API_KEY=your_key_here  # if using Gemini

# PostgreSQL Configuration (for dev profile)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=bankparser

# Application Configuration
APP_NAME=Bank Statement Parser
DEBUG=True
HOST=localhost
PORT=8000

# File Processing Configuration
MAX_FILE_SIZE_MB=10

# LLM Configuration
MODEL_NAME=gpt-4o
MAX_TOKENS=4000
TEMPERATURE=0.1
```

Settings are managed via `app/config.py` using `pydantic-settings` with singleton pattern.

### Database

A PostgreSQL 16 database is included in the `dev` profile for local development:

- **Service name**: `postgres`
- **Port**: 5432
- **Default credentials**: `postgres/postgres`
- **Default database**: `bankparser`
- **Data persistence**: Uses `postgres_data` named volume for persistent storage

The database is currently available but not yet integrated into the application. The app currently operates statelessly, processing PDFs and returning JSON responses without database storage.

## Important Implementation Details

### JSON Mode for GPT-4

The `BaseLLMService._is_json_mode_supported()` method determines if a model supports `response_format={"type": "json_object"}`. Currently only GPT-4o, GPT-4.1, and GPT-4.1-mini are flagged as supporting JSON mode. Update this heuristic when adding new models.

### Multi-Page Statement Handling

When processing multi-page statements:

- **Vision mode**: Each image is processed separately, results are merged with deduplication
- **Text mode**: Full text is sent in one call; pagination is handled via `has_more`/`next_page_hint` hints

Merging logic in `BaseLLMService._merge_chunks()` deduplicates transactions by `(date, description, amount)` tuple.

### Error Handling

The application uses a global exception handling system for consistent error responses.

#### Overview

**Location:** `app/core/exceptions/`

**Components:**

1. **Custom Exception Classes** (`base.py`) - Typed exceptions with status codes
2. **Exception Handlers** (`handlers.py`) - Global handlers that catch and format exceptions
3. **Registration** (`main.py:74`) - `register_exception_handlers(app)` registers all handlers

#### Architecture

```
Exception Thrown → Handler Catches → Formats Response → Returns JSON
```

Registration in main.py:
```python
from app.core.exceptions import register_exception_handlers

register_exception_handlers(app)
```

#### Available Exceptions

All exceptions inherit from `AppException` and include:

- `message`: Human-readable error message
- `status_code`: HTTP status code
- `error_code`: Machine-readable code (e.g., "NOT_FOUND")
- `details`: Additional context (dict)

| Exception               | Status | Use Case                              |
| ----------------------- | ------ | ------------------------------------- |
| `NotFoundException`     | 404    | Resource not found in database        |
| `BadRequestException`   | 400    | Invalid request data or parameters    |
| `UnauthorizedException` | 401    | User not authenticated                |
| `ForbiddenException`    | 403    | User authenticated but not authorized |
| `ConflictException`     | 409    | Resource already exists (duplicate)   |
| `ValidationException`   | 422    | Business logic validation failed      |
| `AppException`          | Custom | Base class for custom exceptions      |

#### Usage Example

```python
from app.core.exceptions import NotFoundException, BadRequestException

# In service layer
def get_project(db: Session, project_id: str):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise NotFoundException(
            message=f"Project with ID {project_id} not found",
            details={"project_id": project_id}
        )

    if not project.is_activated:
        raise BadRequestException(
            message="Cannot access deactivated project",
            details={"project_id": project_id, "status": "inactive"}
        )

    return project
```

**Resulting Error Response:**

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

#### Exception Handlers

Five automatic handlers are registered:

**1. AppException Handler**

- Catches: All custom exceptions (NotFoundException, etc.)
- Returns: Structured JSON with error details
- Logs: WARNING level with context

**2. RequestValidationError Handler** (Pydantic Validation)

- Catches: Invalid request body, query params, path params
- Returns: Field-level validation errors

Example response:

```json
{
  "success": false,
  "error": "Validation failed",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "errors": [
      {
        "field": "body.name",
        "message": "String should have at least 1 characters",
        "type": "string_too_short"
      }
    ]
  }
}
```

**3. IntegrityError Handler** (Database Constraints)

- Catches: Unique constraint, foreign key violations
- Returns: User-friendly error message
- Detects: "unique constraint" → "Resource already exists"
- Detects: "foreign key constraint" → "Related resource not found"

**4. SQLAlchemyError Handler** (General DB Errors)

- Catches: Connection errors, query errors, etc.
- Returns: Generic database error (500)
- Logs: ERROR level with full exception

**5. General Exception Handler** (Catch-All)

- Catches: Any unhandled exception
- Returns: Generic error message
- Logs: ERROR level with full stack trace
- Debug mode: Includes exception details and traceback
- Production mode: Generic "An unexpected error occurred"

#### Debug vs Production Mode

Controlled by `DEBUG` environment variable in `.env`:

**Debug Mode (DEBUG=True):**

```json
{
  "success": false,
  "error": "UNIQUE constraint failed: projects.name",
  "error_code": "DATABASE_ERROR",
  "details": {
    "db_error": "UNIQUE constraint failed: projects.name",
    "exception_type": "IntegrityError",
    "traceback": "Traceback (most recent call last):\n..."
  }
}
```

**Production Mode (DEBUG=False):**

```json
{
  "success": false,
  "error": "Resource already exists",
  "error_code": "DATABASE_CONSTRAINT_VIOLATION",
  "details": {},
  "path": "/api/v1/projects"
}
```

#### Creating Custom Exceptions

1. Define in `app/core/exceptions/base.py`:

```python
class ProjectDeactivatedException(AppException):
    def __init__(self, project_name: str):
        super().__init__(
            message=f"Project '{project_name}' is deactivated",
            status_code=400,
            error_code="PROJECT_DEACTIVATED",
            details={"project_name": project_name}
        )
```

2. Export in `app/core/exceptions/__init__.py`:

```python
from .base import ProjectDeactivatedException

__all__ = [..., "ProjectDeactivatedException"]
```

3. Use anywhere:

```python
from app.core.exceptions import ProjectDeactivatedException

if not project.is_activated:
    raise ProjectDeactivatedException(project.name)
```

Handler will automatically catch and format it!

#### Best Practices

**DO:**

- ✅ Use specific exception types (NotFoundException vs generic Exception)
- ✅ Include helpful details dict for debugging
- ✅ Use ValidationException for business logic failures
- ✅ Let database errors bubble up (handlers will format them)

**DON'T:**

- ❌ Catch exceptions and return custom responses (use raise instead)
- ❌ Use generic Exception() (use AppException or specific types)
- ❌ Expose sensitive data in error messages (passwords, keys, etc.)
- ❌ Include stack traces in production (let DEBUG flag control this)

**Example:**

```python
# BAD ❌
try:
    project = db.query(Project).filter(...).first()
    if not project:
        return {"error": "Not found"}  # Inconsistent format
except Exception as e:
    return {"error": str(e)}  # Generic, no structure

# GOOD ✅
project = db.query(Project).filter(...).first()
if not project:
    raise NotFoundException(f"Project {id} not found")
# Handler automatically formats it correctly!
```

#### Logging

All exceptions are automatically logged with structured data:

```python
# Example log output
WARNING [app.core.exceptions.handlers] AppException: NOT_FOUND - Project with ID 123 not found
  path=/api/v1/projects/123
  method=GET
  status_code=404
  error_code=NOT_FOUND
```

Unhandled exceptions log with full stack trace:

```python
ERROR [app.core.exceptions.handlers] Unhandled exception: division by zero
  path=/api/v1/projects
  method=POST
  exception_type=ZeroDivisionError
  traceback=Traceback (most recent call last)...
  exc_info=True
```

#### Integration with Parser Service

Note: The existing parser service (`app/services/parser_service.py`) returns `ParsedResponse` objects with `success=False` instead of raising exceptions. This is intentional for that service to track processing time even on errors.

**New CRUD features should use exceptions**, not ParsedResponse:

```python
# Parser service (existing pattern - keep as-is)
return ParsedResponse(success=False, error=str(e), processing_time=elapsed)

# CRUD features (new pattern - use exceptions)
raise NotFoundException("Project not found")  # Handler formats response
```

#### Complete Documentation

See `app/core/exceptions/README.md` for:

- Full exception reference
- More usage examples
- Testing exception handling
- Migration guide from old code

## Testing Strategy

While the repository doesn't have extensive tests currently, when adding tests:

1. Mock LLM API calls to avoid costs and ensure deterministic results
2. Use `pytest-asyncio` for async endpoint testing
3. Test each interface implementation independently
4. Use example PDFs in a `tests/fixtures/` directory

Example test structure:

```python
@pytest.mark.asyncio
async def test_parse_statement_success(mock_openai):
    service = BankStatementParserFactory.create_openai_vision_parser()
    result = await service.parse_statement(test_file, use_vision=True)
    assert result.success is True
```

## Common Development Tasks

### Switching LLM Providers

In code:

```python
# Change from OpenAI to Claude
parser = BankStatementParserFactory.create_claude_parser()  # instead of create_openai_vision_parser()
```

Via API:

```bash
curl -X POST "http://localhost:8000/api/v1/parse-statement?llm_provider=claude" ...
```

### Debugging JSON Parsing Issues

If an LLM returns malformed JSON:

1. Check `BaseLLMService._parse_response_json()` - it tries multiple cleanup strategies
2. Add logging to see the raw LLM response before parsing
3. The error will propagate through `ParsedResponse` with the raw error message

### Adding Support for New Banks

The parser is bank-agnostic - the LLM handles format variations. However, if you need bank-specific logic:

1. Add a `BankDetector` service to identify the bank from the PDF
2. Create bank-specific prompts or post-processing logic
3. Inject these as strategies in the parser service

### Modifying the Output Schema

If you need to change the `BankStatement` structure:

1. Update `app/models.py` data models
2. Update the JSON schema in `BaseLLMService._get_parsing_prompt()`
3. Update `BaseLLMService._convert_to_bank_statement()` if field mappings change
4. Ensure all LLM implementations still work with the new schema

## CRUD Features

The application includes comprehensive CRUD APIs for managing projects, bank accounts, categories, and statements.

### Projects CRUD

**Location:** `app/features/projects/`

Projects are the root entity - each real estate project has bank accounts, statements, and transactions.

**API Endpoints:**
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project by ID
- `GET /api/v1/projects` - List projects (paginated)
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Soft delete (sets is_activated=False)

**Features:**
- Soft delete using `is_activated` field
- Pagination (max 100 items per page)
- Search by project name
- Filter by activation status
- Ordered by created_at desc

**Fields:**
- name, developer_name, investor_name, remarks
- is_activated (soft delete flag)
- Audit fields: created_by, created_at, updated_at, updated_by

**Test Coverage:** 32 tests (13 unit + 19 integration)

### Bank Accounts CRUD

**Location:** `app/features/accounts/`

Bank accounts belong to projects. Each account can have multiple statement files.

**API Endpoints:**
- `POST /api/v1/accounts` - Create account
- `GET /api/v1/accounts/{id}` - Get account by ID
- `GET /api/v1/accounts` - List accounts (paginated)
- `PUT /api/v1/accounts/{id}` - Update account
- `DELETE /api/v1/accounts/{id}` - Hard delete

**Features:**
- Foreign key validation (validates project_id exists)
- Search by bank name or account number
- Filter by project_id and account_type
- Pagination support

**Fields:**
- project_id (FK to projects)
- account_number (last 4 digits)
- bank_name, account_type
- color, position_x, position_y (for UI visualization)
- Audit fields: created_by, created_at, updated_at, updated_by

**Test Coverage:** 32 tests (14 unit + 18 integration)

### Categories CRUD

**Location:** `app/features/categories/`

Categories are master data for transaction categorization with regex-based auto-matching.

**API Endpoints:**
- `POST /api/v1/categories` - Create category
- `GET /api/v1/categories/{id}` - Get category by ID
- `GET /api/v1/categories` - List categories (paginated)
- `PUT /api/v1/categories/{id}` - Update category
- `DELETE /api/v1/categories/{id}` - Soft delete (sets is_active=False)

**Features:**
- Soft delete using `is_active` field
- Auto-categorization via `identification_regex`
- Search by name or description (case-insensitive)
- Filter by activation status

**Fields:**
- name, identification_regex, color, description
- is_active (soft delete flag)
- Audit fields: created_by, created_at, updated_at, updated_by

**Test Coverage:** 34 tests (13 unit + 21 integration)

### Bank Statement Files CRUD

**Location:** `app/features/statement_files/`

Statement files represent uploaded PDF files stored in Azure Blob Storage.

**API Endpoints:**
- `POST /api/v1/statement-files` - Create statement file record
- `GET /api/v1/statement-files/{id}` - Get file by ID
- `GET /api/v1/statement-files` - List files (paginated)
- `PUT /api/v1/statement-files/{id}` - Update file metadata
- `DELETE /api/v1/statement-files/{id}` - Hard delete

**Features:**
- Foreign key validation (bank_account_id)
- Period validation (period_end >= period_start)
- Filter by bank account
- Search by file path

**Fields:**
- bank_account_id (FK to bank_accounts)
- file_path (Azure Blob Storage URL)
- period_start, period_end (statement period)
- Audit fields: uploaded_by, uploaded_at, updated_at, updated_by

**Test Coverage:** 34 tests (13 unit + 21 integration)

### Bank Statement Entries CRUD

**Location:** `app/features/statement_entries/`

Statement entries are individual transactions extracted from statement files.

**API Endpoints:**
- `POST /api/v1/statement-entries` - Create entry
- `GET /api/v1/statement-entries/{id}` - Get entry by ID
- `GET /api/v1/statement-entries` - List entries (paginated)
- `PUT /api/v1/statement-entries/{id}` - Update entry
- `DELETE /api/v1/statement-entries/{id}` - Hard delete (cascades to splits)

**Features:**
- Foreign key validation (file, account, category)
- Amount validation (must be > 0)
- Comprehensive filtering (account, file, category, type, search)
- Order by date desc, created_at desc

**Fields:**
- bank_statement_file_id, bank_account_id, category_id (FKs)
- tags_csv (JSONB array of free-form tags)
- date, time, description, transaction_reference
- debit_credit (enum: debit/credit)
- amount, balance, notes
- Audit fields: created_at, updated_at, modified_by, updated_by

**Filters:**
- bank_account_id, bank_statement_file_id, category_id
- transaction_type (debit/credit)
- search (description, transaction_reference)

### Entry Splits CRUD

**Location:** `app/features/entry_splits/`

Entry splits allow splitting a single transaction across multiple categories.

**API Endpoints:**
- `POST /api/v1/entry-splits` - Create split
- `GET /api/v1/entry-splits/{id}` - Get split by ID
- `GET /api/v1/entry-splits` - List splits (paginated)
- `PUT /api/v1/entry-splits/{id}` - Update split
- `DELETE /api/v1/entry-splits/{id}` - Hard delete

**Features:**
- Foreign key validation (entry, category)
- Amount validation (must be > 0)
- Filter by entry or category

**Fields:**
- bank_statement_entry_id, category_id (FKs)
- amount, description
- Audit fields: created_at, updated_at, modified_by, updated_by

### CRUD Architecture Patterns

All CRUD features follow consistent patterns:

**1. Three-Layer Architecture:**
```
Routes (API) → Service (Business Logic) → Database (SQLAlchemy)
```

**2. Service Layer Pattern:**
```python
class ProjectService:
    @staticmethod
    def create_project(db: Session, data: ProjectCreateRequest) -> ProjectResponse:
        # Validation, business logic, database operations
        pass
```

**3. Pydantic Schemas:**
- `CreateRequest` - Required fields for creation
- `UpdateRequest` - Optional fields for partial updates
- `Response` - Complete object with all fields
- `ListResponse` - Paginated list with metadata

**4. Global Exception Handling:**
```python
from app.core.exceptions import NotFoundException

raise NotFoundException(
    message=f"Project {id} not found",
    details={"project_id": str(id)}
)
```

**5. Database Patterns:**
- Soft delete: `is_activated` (Projects), `is_active` (Categories)
- Hard delete: Accounts, Files, Entries, Splits
- UUID primary keys
- Audit fields on all tables
- Foreign key constraints with validation

**6. Test Structure:**
- Unit tests: Mock database, test business logic
- Integration tests: Real SQLite DB, test database operations
- Fixtures in `tests/conftest.py`

### Database Relationships

```
Project (1:N) → BankAccount (1:N) → BankStatementFile (1:N) → BankStatementEntry (1:N) → BankStatementEntrySplit
                                                                       ↓
                                                                  Category
```

### Common CRUD Patterns

**Creating with Foreign Key:**
```python
# Validate parent exists
bank_account = db.query(BankAccount).filter(BankAccount.id == data.bank_account_id).first()
if not bank_account:
    raise NotFoundException("Bank account not found")

# Create child
entry = BankStatementEntry(**data.dict())
db.add(entry)
db.commit()
```

**Pagination:**
```python
# Validate pagination params
if page < 1:
    raise BadRequestException("Page number must be greater than 0")

# Apply pagination
query.offset((page - 1) * page_size).limit(page_size).all()
total_pages = ceil(total / page_size)
```

**Partial Updates:**
```python
# Only update provided fields
update_data = data.model_dump(exclude_unset=True)
for field, value in update_data.items():
    setattr(entity, field, value)
entity.updated_at = datetime.utcnow()
```

**Search & Filter:**
```python
# Case-insensitive search
search_filter = f"%{search}%"
query = query.filter(Entity.name.ilike(search_filter))

# Boolean filter
if is_active is not None:
    query = query.filter(Entity.is_active == is_active)
```
