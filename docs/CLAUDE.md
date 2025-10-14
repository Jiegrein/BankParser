# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
# Build and run
docker-compose up --build

# Build only
docker build -t bank-parser .

# Run container
docker run -p 8000:8000 --env-file .env bank-parser
```

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
OPENAI_API_KEY=your_key_here
CLAUDE_API_KEY=your_key_here  # if using Claude
GEMINI_API_KEY=your_key_here  # if using Gemini

APP_NAME=Bank Statement Parser
DEBUG=True
HOST=localhost
PORT=8000

MAX_FILE_SIZE_MB=10
MODEL_NAME=gpt-4o
MAX_TOKENS=4000
TEMPERATURE=0.1
```

Settings are managed via `app/config.py` using `pydantic-settings` with singleton pattern.

## Important Implementation Details

### JSON Mode for GPT-4

The `BaseLLMService._is_json_mode_supported()` method determines if a model supports `response_format={"type": "json_object"}`. Currently only GPT-4o, GPT-4.1, and GPT-4.1-mini are flagged as supporting JSON mode. Update this heuristic when adding new models.

### Multi-Page Statement Handling

When processing multi-page statements:
- **Vision mode**: Each image is processed separately, results are merged with deduplication
- **Text mode**: Full text is sent in one call; pagination is handled via `has_more`/`next_page_hint` hints

Merging logic in `BaseLLMService._merge_chunks()` deduplicates transactions by `(date, description, amount)` tuple.

### Error Handling

The parser service returns `ParsedResponse` objects with `success=False` and error details rather than raising exceptions. This allows the API to return structured error responses with processing time metrics.

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
