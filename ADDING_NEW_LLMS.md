# Adding New LLM Providers - Developer Guide

## 🔌 Drop-in LLM Integration

This architecture makes it **incredibly easy** to add new LLM providers. Here's exactly how minimal the code changes are:

## ✅ **What You Need to Do (3 Simple Steps)**

### **Step 1: Implement the Interface**
Create a new class implementing `LLMServiceInterface`:

```python
from app.services.llm_service import LLMServiceInterface

class YourNewLLMService(LLMServiceInterface):
    async def parse_text_statement(self, text_content: str) -> BankStatement:
        # Your LLM's text processing logic here
        pass
    
    async def parse_image_statement(self, base64_images: List[str]) -> BankStatement:
        # Your LLM's vision processing logic here  
        pass
```

### **Step 2: Add to Factory**
Add one method to `LLMServiceFactory`:

```python
@staticmethod
def create_your_llm_service() -> LLMServiceInterface:
    return YourNewLLMService()
```

### **Step 3: Add to Parser Factory**
Add one method to `BankStatementParserFactory`:

```python
@staticmethod
def create_your_llm_parser() -> BankStatementParserService:
    return BankStatementParserService(
        pdf_processor=PDFProcessorFactory.create_image_processor(),
        llm_service=LLMServiceFactory.create_your_llm_service()
    )
```

## 🚫 **What You DON'T Need to Change**

- ❌ **No changes** to core parsing logic
- ❌ **No changes** to API routes (optional)
- ❌ **No changes** to data models
- ❌ **No changes** to PDF processing
- ❌ **No changes** to file validation
- ❌ **No changes** to error handling

## 🧩 **Architecture Benefits**

### **Interface Segregation**
```python
# Clean, focused interface
class LLMServiceInterface(ABC):
    @abstractmethod
    async def parse_text_statement(self, text_content: str) -> BankStatement:
        pass
    
    @abstractmethod  
    async def parse_image_statement(self, base64_images: List[str]) -> BankStatement:
        pass
```

### **Dependency Inversion**
```python
# High-level modules depend on abstractions
class BankStatementParserService:
    def __init__(self, llm_service: LLMServiceInterface):
        self.llm_service = llm_service  # Any implementation works!
```

### **Strategy Pattern**
```python
# Runtime LLM selection
def get_parser_service(llm_provider: str):
    if llm_provider == "openai":
        return BankStatementParserFactory.create_openai_parser()
    elif llm_provider == "claude":
        return BankStatementParserFactory.create_claude_parser()
    elif llm_provider == "your_llm":
        return BankStatementParserFactory.create_your_llm_parser()
```

## 📋 **Complete Example: Adding Ollama**

Here's a complete example adding Ollama (local LLM) support:

```python
# 1. Create the service
class OllamaService(LLMServiceInterface):
    def __init__(self):
        import ollama
        self.client = ollama.Client()
    
    async def parse_text_statement(self, text_content: str) -> BankStatement:
        response = self.client.generate(
            model='llama2',
            prompt=f"{self._get_parsing_prompt()}\n\n{text_content}"
        )
        
        json_content = response['response']
        parsed_data = json.loads(json_content)
        return self._convert_to_bank_statement(parsed_data)
    
    async def parse_image_statement(self, base64_images: List[str]) -> BankStatement:
        # Use LLaVA or similar vision model
        response = self.client.generate(
            model='llava',
            prompt=self._get_parsing_prompt(),
            images=base64_images
        )
        # ... process response

# 2. Add to factory
class LLMServiceFactory:
    @staticmethod
    def create_ollama_service() -> LLMServiceInterface:
        return OllamaService()

# 3. Add to parser factory  
class BankStatementParserFactory:
    @staticmethod
    def create_ollama_parser() -> BankStatementParserService:
        return BankStatementParserService(
            llm_service=LLMServiceFactory.create_ollama_service()
        )

# 4. Use it (optional API route update)
@router.post("/parse-statement")
async def parse_bank_statement(
    file: UploadFile,
    llm_provider: str = "openai"  # Now supports "ollama" too!
):
    if llm_provider == "ollama":
        parser = BankStatementParserFactory.create_ollama_parser()
    else:
        parser = BankStatementParserFactory.create_default_parser()
    
    return await parser.parse_statement(file)
```

## 🎯 **Real-World Examples**

### **OpenAI → Claude Switch**
```python
# Before (OpenAI)
parser = BankStatementParserFactory.create_openai_parser()

# After (Claude) - ONE LINE CHANGE
parser = BankStatementParserFactory.create_claude_parser()

# Core logic stays the same!
result = await parser.parse_statement(file)
```

### **A/B Testing Multiple LLMs**
```python
# Test different LLMs with same data
openai_result = await BankStatementParserFactory.create_openai_parser().parse_statement(file)
claude_result = await BankStatementParserFactory.create_claude_parser().parse_statement(file)
ollama_result = await BankStatementParserFactory.create_ollama_parser().parse_statement(file)

# Compare accuracy, speed, cost, etc.
```

### **Fallback Strategy**
```python
async def parse_with_fallback(file):
    try:
        # Try primary LLM
        return await BankStatementParserFactory.create_openai_parser().parse_statement(file)
    except Exception:
        # Fallback to secondary LLM
        return await BankStatementParserFactory.create_claude_parser().parse_statement(file)
```

## 🔥 **Key Architecture Wins**

1. **Single Responsibility**: Each LLM service only handles one LLM
2. **Open/Closed**: Open for new LLMs, closed for modification  
3. **Liskov Substitution**: Any LLM can replace any other LLM
4. **Interface Segregation**: Clean, minimal interface
5. **Dependency Inversion**: Depend on abstractions, not implementations

## 🚀 **Adding Your LLM Provider**

See `example_new_llm.py` for a complete working example with:
- Local Llama implementation
- Mock responses for testing
- Integration examples
- Usage demonstrations

**The architecture makes adding new LLMs trivial - that was the whole point!** 🎯