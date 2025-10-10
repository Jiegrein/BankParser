from abc import ABC, abstractmethod
from typing import List, Dict, Any
import openai
import json
# import anthropic  # Uncomment when adding Claude
from app.models import BankStatement, Transaction
from app.config import get_settings


class LLMServiceInterface(ABC):
    """Interface for LLM services (Interface Segregation Principle)"""
    
    @abstractmethod
    async def parse_text_statement(self, text_content: str) -> BankStatement:
        """Parse bank statement from text"""
        pass
    
    @abstractmethod
    async def parse_image_statement(self, base64_images: List[str]) -> BankStatement:
        """Parse bank statement from images"""
        pass


class OpenAIService(LLMServiceInterface):
    """OpenAI GPT service implementation (Single Responsibility Principle)"""
    
    def __init__(self):
        self.settings = get_settings()
        openai.api_key = self.settings.openai_api_key
        self.client = openai.OpenAI(api_key=self.settings.openai_api_key)
    
    def _get_parsing_prompt(self) -> str:
        """Get the standard parsing prompt"""
        return """
        You are a bank statement parsing expert. Extract and standardize the following bank statement data into the specified JSON format.

        Required fields:
        - account_holder: Full name of the account holder
        - bank_name: Name of the bank
        - account_number: Account number (keep last 4 digits visible, mask others with *)
        - statement_period: Object with start_date and end_date (YYYY-MM-DD format)
        - opening_balance: Starting balance as a number
        - closing_balance: Ending balance as a number
        - transactions: Array of transaction objects

        For each transaction, include:
        - date: Transaction date (YYYY-MM-DD format)
        - description: Transaction description
        - amount: Transaction amount (positive number)
        - type: "credit" or "debit"
        - category: Transaction category (optional)
        - balance: Running balance after transaction (optional)

        Return ONLY valid JSON without any markdown formatting or explanations.
        
        Example format:
        {
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
        }
        After extraction ensure that for all transactions balance matches the previous transaction + deposited or withdrawn amount in that transaction, also validate your extraction by checking opening and closing balance. It is absolutely critical that you extract all details properly and do not reorder or skip a transaction or you will lose your job
        """
    
    async def parse_text_statement(self, text_content: str) -> BankStatement:
        """Parse bank statement from text using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.settings.model_name.replace("-vision-preview", ""),  # Use text model
                messages=[
                    {"role": "system", "content": self._get_parsing_prompt()},
                    {"role": "user", "content": f"Parse this bank statement:\n\n{text_content}"}
                ],
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature
            )
            
            # Extract JSON from response
            json_content = response.choices[0].message.content.strip()
            
            # Parse JSON and validate
            parsed_data = json.loads(json_content)
            
            # Convert to BankStatement model
            return self._convert_to_bank_statement(parsed_data)
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to parse statement with OpenAI: {str(e)}")
    
    async def parse_image_statement(self, base64_images: List[str]) -> BankStatement:
        """Parse bank statement from images using OpenAI Vision"""
        try:
            # Prepare messages with images
            messages = [
                {"role": "system", "content": self._get_parsing_prompt()}
            ]
            
            # Add user message with images
            user_content = [
                {"type": "text", "text": "Parse this bank statement from the provided images:"}
            ]
            
            for base64_image in base64_images:
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                })
            
            messages.append({"role": "user", "content": user_content})
            
            response = self.client.chat.completions.create(
                model=self.settings.model_name,
                messages=messages,
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature
            )
            
            # Extract JSON from response
            json_content = response.choices[0].message.content.strip()
            
            # Parse JSON and validate
            parsed_data = json.loads(json_content)
            
            # Convert to BankStatement model
            return self._convert_to_bank_statement(parsed_data)
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to parse statement with OpenAI Vision: {str(e)}")
    
    def _convert_to_bank_statement(self, data: Dict[str, Any]) -> BankStatement:
        """Convert parsed data to BankStatement model"""
        try:
            # Convert transactions
            transactions = []
            for txn_data in data.get("transactions", []):
                transaction = Transaction(
                    date=txn_data["date"],
                    description=txn_data["description"],
                    amount=float(txn_data["amount"]),
                    type=txn_data["type"],
                    category=txn_data.get("category"),
                    balance=float(txn_data["balance"]) if txn_data.get("balance") else None
                )
                transactions.append(transaction)
            
            # Create BankStatement
            bank_statement = BankStatement(
                account_holder=data["account_holder"],
                bank_name=data["bank_name"],
                account_number=data["account_number"],
                statement_period=data["statement_period"],
                opening_balance=float(data["opening_balance"]),
                closing_balance=float(data["closing_balance"]),
                transactions=transactions,
                currency=data.get("currency", "USD")
            )
            
            return bank_statement
            
        except Exception as e:
            raise Exception(f"Failed to convert data to BankStatement model: {str(e)}")


class LLMServiceFactory:
    """Factory for creating LLM services (Factory Pattern)"""
    
    @staticmethod
    def create_openai_service() -> LLMServiceInterface:
        """Create OpenAI service"""
        return OpenAIService()
    
    @staticmethod
    def create_claude_service() -> LLMServiceInterface:
        """Create Claude service"""
        return ClaudeService()
    
    @staticmethod
    def create_gemini_service() -> LLMServiceInterface:
        """Create Gemini service"""  
        return GeminiService()
    
    @staticmethod
    def create_default_service() -> LLMServiceInterface:
        """Create default service (OpenAI)"""
        return OpenAIService()


# Example implementations for other LLMs

class ClaudeService(LLMServiceInterface):
    """Claude (Anthropic) service implementation"""
    
    def __init__(self):
        self.settings = get_settings()
        # self.client = anthropic.Anthropic(api_key=self.settings.claude_api_key)
    
    async def parse_text_statement(self, text_content: str) -> BankStatement:
        """Parse bank statement from text using Claude"""
        try:
            # Example Claude implementation
            # response = self.client.messages.create(
            #     model="claude-3-opus-20240229",
            #     max_tokens=4000,
            #     messages=[
            #         {"role": "user", "content": f"{self._get_parsing_prompt()}\n\n{text_content}"}
            #     ]
            # )
            # json_content = response.content[0].text
            
            # For now, raise not implemented
            raise NotImplementedError("Claude implementation pending - add anthropic dependency")
            
        except Exception as e:
            raise Exception(f"Failed to parse statement with Claude: {str(e)}")
    
    async def parse_image_statement(self, base64_images: List[str]) -> BankStatement:
        """Parse bank statement from images using Claude"""
        # Claude 3 supports vision
        raise NotImplementedError("Claude vision implementation pending")
    
    def _get_parsing_prompt(self) -> str:
        """Same prompt as OpenAI - reusable"""
        return OpenAIService()._get_parsing_prompt()


class GeminiService(LLMServiceInterface):
    """Google Gemini service implementation"""
    
    def __init__(self):
        self.settings = get_settings()
        # import google.generativeai as genai
        # genai.configure(api_key=self.settings.gemini_api_key)
        # self.model = genai.GenerativeModel('gemini-pro-vision')
    
    async def parse_text_statement(self, text_content: str) -> BankStatement:
        """Parse bank statement from text using Gemini"""
        raise NotImplementedError("Gemini implementation pending - add google-generativeai dependency")
    
    async def parse_image_statement(self, base64_images: List[str]) -> BankStatement:
        """Parse bank statement from images using Gemini"""
        raise NotImplementedError("Gemini vision implementation pending")