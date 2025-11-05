# Bank Statement Parser

A FastAPI-based API for parsing bank statements from PDF files using OpenAI's GPT models.

## Features

### AI-Powered Statement Parsing
- 📄 **PDF Processing**: Upload PDF bank statements from any bank
- 🤖 **AI-Powered**: Uses GPT-4 Vision for accurate parsing
- 🏛️ **Multi-Bank Support**: Works with statements from different banks
- 📊 **Standardized Output**: Consistent JSON format regardless of source bank
- ⚡ **Fast Processing**: Quick turnaround time

### Complete CRUD APIs
- 🏢 **Projects Management**: CRUD for real estate projects
- 🏦 **Bank Accounts**: Manage accounts under projects
- 🏷️ **Categories**: Transaction categorization with regex matching
- 📁 **Statement Files**: Track uploaded PDF files
- 💰 **Transactions**: Individual statement entries with splits
- 🔍 **Advanced Filtering**: Search, pagination, and multi-field filtering

### Architecture & Infrastructure
- 🗄️ **PostgreSQL Database**: Full relational database with migrations
- 🐳 **Docker Support**: Production & dev containers with auto-migrations
- 🔒 **Global Exception Handling**: Consistent error responses
- 🧪 **Comprehensive Tests**: 132+ passing tests
- 🏗️ **SOLID Principles**: Clean, maintainable architecture
- 📝 **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone or download this repository
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. Run the application:

   ```bash
   python main.py
   ```

   Or directly:

   ```bash
   uvicorn main:app --reload
   ```

5. Open your browser to `http://localhost:8000/docs` to see the API documentation

### Docker

```bash
# Build and run
docker-compose up --build

# Or manually
docker build -t bank-parser .
docker run -p 8000:8000 --env-file .env bank-parser
```

See [docs/DOCKER.md](docs/DOCKER.md) for comprehensive Docker deployment guide.

## API Usage

### Parse Bank Statement

**Endpoint**: `POST /api/v1/parse-statement`

**Parameters**:

- `file`: PDF file (required)
- `use_vision`: Boolean (optional, default: true)
- `llm_provider`: String (optional, default: "openai") - Choose from: openai, claude, gemini

**Example using curl**:

```bash
curl -X POST "http://localhost:8000/api/v1/parse-statement?use_vision=true&llm_provider=openai" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@bank_statement.pdf"
```

**Response Format**:

```json
{
  "success": true,
  "data": {
    "account_holder": "John Doe",
    "bank_name": "Chase Bank",
    "account_number": "****1234",
    "statement_period": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    },
    "opening_balance": 2500.0,
    "closing_balance": 2750.0,
    "transactions": [
      {
        "date": "2024-01-05",
        "description": "Direct Deposit - Salary",
        "amount": 3000.0,
        "type": "credit",
        "category": "income"
      }
    ],
    "currency": "USD"
  },
  "processing_time": 5.23
}
```

## CRUD API Endpoints

The application provides comprehensive REST APIs for managing projects, accounts, and transactions:

### Projects API
```bash
POST   /api/v1/projects          # Create project
GET    /api/v1/projects          # List projects (paginated)
GET    /api/v1/projects/{id}     # Get project by ID
PUT    /api/v1/projects/{id}     # Update project
DELETE /api/v1/projects/{id}     # Soft delete project
```

### Bank Accounts API
```bash
POST   /api/v1/accounts          # Create account
GET    /api/v1/accounts          # List accounts (paginated)
GET    /api/v1/accounts/{id}     # Get account by ID
PUT    /api/v1/accounts/{id}     # Update account
DELETE /api/v1/accounts/{id}     # Delete account
```

### Categories API
```bash
POST   /api/v1/categories        # Create category
GET    /api/v1/categories        # List categories (paginated)
GET    /api/v1/categories/{id}   # Get category by ID
PUT    /api/v1/categories/{id}   # Update category
DELETE /api/v1/categories/{id}   # Soft delete category
```

### Statement Files API
```bash
POST   /api/v1/statement-files           # Create statement file
GET    /api/v1/statement-files           # List files (paginated)
GET    /api/v1/statement-files/{id}      # Get file by ID
PUT    /api/v1/statement-files/{id}      # Update file
DELETE /api/v1/statement-files/{id}      # Delete file
```

### Statement Entries API
```bash
POST   /api/v1/statement-entries         # Create entry
GET    /api/v1/statement-entries         # List entries (paginated, filterable)
GET    /api/v1/statement-entries/{id}    # Get entry by ID
PUT    /api/v1/statement-entries/{id}    # Update entry
DELETE /api/v1/statement-entries/{id}    # Delete entry
```

### Entry Splits API
```bash
POST   /api/v1/entry-splits              # Create split
GET    /api/v1/entry-splits              # List splits (paginated)
GET    /api/v1/entry-splits/{id}         # Get split by ID
PUT    /api/v1/entry-splits/{id}         # Update split
DELETE /api/v1/entry-splits/{id}         # Delete split
```

**All endpoints support:**
- Pagination (page, page_size)
- Filtering by various fields
- Search functionality
- Consistent error responses

**Full API documentation:** http://localhost:8000/docs

## Configuration

Edit `.env` file to configure:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Other LLM providers
CLAUDE_API_KEY=your_claude_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

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

## Supported Banks

The API works with bank statements from major banks including:

- Chase Bank
- Bank of America
- Wells Fargo
- Citibank
- Capital One
- US Bank
- And many more...

## Documentation

- **[CLAUDE.md](docs/CLAUDE.md)** - Comprehensive guide for AI assistants working with this codebase
- **[ADDING_NEW_LLMS.md](docs/ADDING_NEW_LLMS.md)** - Developer guide for integrating new LLM providers
- **[DOCKER.md](docs/DOCKER.md)** - Complete Docker deployment guide with examples
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## Architecture

This project follows SOLID principles with a clean, extensible architecture:

- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable for their base types
- **Interface Segregation**: Many client-specific interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

### Project Structure

```
BankStatementParser/
├── app/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── services/
│   │   ├── parser_service.py  # Main orchestration
│   │   ├── llm/               # LLM service implementations
│   │   │   ├── interface.py
│   │   │   ├── base.py        # Shared LLM logic
│   │   │   ├── openai_service.py
│   │   │   ├── claude_service.py
│   │   │   └── gemini_service.py
│   │   ├── pdf/               # PDF processing
│   │   │   ├── interface.py
│   │   │   ├── text_extractor.py
│   │   │   └── image_extractor.py
│   │   └── validation/        # File validation
│   ├── models.py              # Data models (Pydantic)
│   └── config.py              # Configuration settings
├── docs/                      # Documentation
├── main.py                    # FastAPI app
└── requirements.txt           # Dependencies
```

## Development

To extend the application:

1. **Add new PDF processors**: Implement `PDFProcessorInterface`
2. **Add new LLM services**: Implement `LLMServiceInterface` (see [docs/ADDING_NEW_LLMS.md](docs/ADDING_NEW_LLMS.md))
3. **Add new validators**: Implement validation interfaces
4. **Modify parsing logic**: Edit `BankStatementParserService`

### Development Commands

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Format code
black .
isort .

# Lint
flake8 app/
mypy app/

# Run tests
pytest
pytest --cov=app --cov-report=html
```

## License

This project is open source and available under the MIT License.
