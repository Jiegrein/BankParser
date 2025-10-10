# Bank Statement Parser

A FastAPI-based API for parsing bank statements from PDF files using OpenAI's GPT models.

## Features

- 📄 **PDF Processing**: Upload PDF bank statements from any bank
- 🤖 **AI-Powered**: Uses GPT-4 Vision for accurate parsing
- 🏛️ **Multi-Bank Support**: Works with statements from different banks
- 📊 **Standardized Output**: Consistent JSON format regardless of source bank
- ⚡ **Fast Processing**: Quick turnaround time
- 🔒 **Secure**: File validation and error handling
- 🏗️ **SOLID Principles**: Clean, maintainable architecture

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
   python run.py
   ```
   
   Or directly:
   ```bash
   uvicorn main:app --reload
   ```

5. Open your browser to `http://localhost:8000/docs` to see the API documentation

## API Usage

### Parse Bank Statement

**Endpoint**: `POST /api/v1/parse-statement`

**Parameters**:
- `file`: PDF file (required)
- `use_vision`: Boolean (optional, default: true)

**Example using curl**:
```bash
curl -X POST "http://localhost:8000/api/v1/parse-statement?use_vision=true" \
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
    "opening_balance": 2500.00,
    "closing_balance": 2750.00,
    "transactions": [
      {
        "date": "2024-01-05",
        "description": "Direct Deposit - Salary",
        "amount": 3000.00,
        "type": "credit",
        "category": "income"
      }
    ],
    "currency": "USD"
  },
  "processing_time": 5.23
}
```

## Architecture

This project follows SOLID principles:

- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable for their base types
- **Interface Segregation**: Many client-specific interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

### Project Structure

```
BankParser/
├── app/
│   ├── __init__.py
│   ├── models.py              # Data models (Pydantic)
│   ├── config.py              # Configuration settings
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API routes
│   └── services/
│       ├── __init__.py
│       ├── pdf_processor.py   # PDF processing logic
│       ├── llm_service.py     # LLM integration
│       ├── file_validator.py  # File validation
│       └── parser_service.py  # Main parsing orchestration
├── main.py                    # FastAPI app
├── run.py                     # Application runner
├── requirements.txt           # Dependencies
├── .env                       # Environment variables
└── README.md                  # This file
```

## Configuration

Edit `.env` file to configure:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Application Configuration
APP_NAME=Bank Statement Parser
DEBUG=True
HOST=localhost
PORT=8000

# File Processing Configuration
MAX_FILE_SIZE_MB=10

# LLM Configuration
MODEL_NAME=gpt-4-vision-preview
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

## Error Handling

The API includes comprehensive error handling for:
- Invalid file types
- File size limits
- Malformed PDFs
- API rate limits
- Processing failures

## Security

- File type validation
- File size limits
- Content validation
- Error message sanitization
- CORS configuration

## Development

To extend the application:

1. **Add new PDF processors**: Implement `PDFProcessorInterface`
2. **Add new LLM services**: Implement `LLMServiceInterface`
3. **Add new validators**: Implement `FileValidatorInterface`
4. **Modify parsing logic**: Edit `BankStatementParserService`

## License

This project is open source and available under the MIT License.