# Troubleshooting Guide

Common issues and their solutions when working with the Bank Statement Parser.

## Docker Issues

### Python Magic Library Error

**Problem**: `python-magic-bin==0.4.14` is Windows-specific and not available on Linux

**Solution**:
- Use `python-magic==0.4.27` (cross-platform) in requirements.txt
- Add `libmagic-dev` system dependency in Dockerfile
- The Dockerfile already includes these fixes

### Dockerfile Build Warnings

**Problem**: Warning about FROM/AS keyword casing mismatch

**Solution**: Use consistent uppercase keywords:
```dockerfile
FROM python:3.13-slim AS base
```

### Container Won't Start

**Check logs**:
```bash
docker logs bankparser
```

**Verify port availability**:
```bash
# Linux/Mac
netstat -tlnp | grep 8000

# Windows
netstat -an | findstr :8000
```

**Verify environment variables**:
```bash
docker exec bankparser env | grep OPENAI
```

### Volume Mounting Not Working (Windows)

Make sure Docker Desktop has access to your drive:
1. Open Docker Desktop
2. Go to Settings → Resources → File Sharing
3. Add your drive (e.g., C:)
4. Apply & Restart

## Pydantic Configuration Issues

### BaseSettings Import Error

**Error**: `pydantic.errors.PydanticImportError: BaseSettings has been moved to pydantic-settings package`

**Solution**: Already fixed in `app/config.py`:
```python
from pydantic_settings import BaseSettings  # ✅ Correct
# NOT: from pydantic import BaseSettings     # ❌ Old way
```

Make sure `pydantic-settings==2.1.0` is in requirements.txt.

### Protected Namespace Warning

**Problem**: Warning about `model_` prefix being protected

**Solution**: Already configured in `app/config.py`:
```python
model_config = {
    "protected_namespaces": ('settings_',)  # Allows 'model_' prefix
}
```

## LLM API Issues

### OpenAI API Key Not Found

**Check environment**:
```bash
# Verify .env file exists and contains key
cat .env | grep OPENAI_API_KEY

# In Docker, check if passed correctly
docker exec bankparser env | grep OPENAI_API_KEY
```

### JSON Parsing Errors

If an LLM returns malformed JSON, the `BaseLLMService._parse_response_json()` tries multiple cleanup strategies:
1. Raw parsing
2. Strip markdown code fences
3. Remove trailing commas
4. Normalize number separators (e.g., `1,234.56` → `1234.56`)
5. Extract first JSON object

**Debug**: Add logging to see raw LLM response:
```python
logger.info(f"Raw LLM response: {raw_content}")
```

### Rate Limit Errors

**Symptom**: 429 errors from OpenAI/Claude/Gemini

**Solutions**:
- Implement exponential backoff (not currently in codebase)
- Add rate limiting middleware
- Cache common parsing results

## PDF Processing Issues

### Invalid PDF Error

**Check if file is actually a PDF**:
```python
# The validator checks for PDF magic number
with open(file_path, 'rb') as f:
    header = f.read(4)
    is_pdf = header == b'%PDF'
```

### Image Extraction Fails

**Requirements**:
- `pdf2image` package
- `poppler-utils` system dependency

**Verify poppler is installed**:
```bash
# Linux
which pdftoppm

# Docker
docker exec bankparser which pdftoppm
```

### Text Extraction Returns Empty

Some PDFs are image-based (scanned documents) with no extractable text. Use vision mode instead:
```bash
curl -X POST "http://localhost:8000/api/v1/parse-statement?use_vision=true" ...
```

## File Upload Issues

### File Too Large

**Default limit**: 10MB (configurable in `.env`)

**Change limit**:
```env
MAX_FILE_SIZE_MB=20
```

### File Type Not Supported

Currently only PDFs are supported. Check validation in `app/services/validation/pdf_validator.py`.

## Performance Issues

### Slow Parsing

**Vision mode** (recommended but slower):
- Converts PDF to images (I/O intensive)
- Sends images to vision LLM (API call overhead)
- Typical time: 5-15 seconds per page

**Text mode** (faster but less accurate):
- Extracts text directly
- Single API call
- Typical time: 2-5 seconds

**Optimize**:
- Use text mode for simple, text-based statements
- Implement caching for repeated statements
- Process pages in parallel (not currently implemented)

## Development Issues

### Hot Reload Not Working (Docker Dev Mode)

**Ensure volume is mounted correctly**:
```bash
# Linux/Mac
docker run -v $(pwd):/app bankparser:dev

# Windows PowerShell
docker run -v ${PWD}:/app bankparser:dev
```

**Check uvicorn reload setting** in `main.py`:
```python
uvicorn.run("main:app", reload=True)  # Must be True
```

### Import Errors

**Symptom**: `ModuleNotFoundError` when running locally

**Solution**: Set PYTHONPATH:
```bash
export PYTHONPATH=/path/to/BankStatementParser
python main.py
```

Or use the run script:
```bash
python run.py  # Handles PYTHONPATH automatically
```

## API Response Issues

### Response Contains HTML Instead of JSON

**Cause**: Server error or wrong endpoint

**Check**:
- Endpoint path is correct: `/api/v1/parse-statement`
- Content-Type header is set correctly
- Server is running (check logs)

### Processing Succeeds But No Transactions

**Possible causes**:
1. PDF page doesn't contain transaction data (e.g., summary page, disclaimer page)
2. LLM couldn't extract transactions
3. Transactions are on a different page

**Solution**: The prompt instructs LLMs to return `transactions: []` for non-transaction pages. This is expected behavior.

## Testing Issues

### Tests Not Found

**Current status**: Repository doesn't have extensive tests yet.

**To add tests**:
```bash
mkdir tests
pip install -r requirements-dev.txt
pytest
```

## Need More Help?

1. Check server logs: `docker logs bankparser`
2. Enable debug mode: `DEBUG=True` in `.env`
3. Review API docs: http://localhost:8000/docs
4. Check recent commits for fixes: `git log --oneline`
