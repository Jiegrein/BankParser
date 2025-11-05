"""
Example: Adding a new LLM provider (Local Llama) to the bank statement parser

This file demonstrates how easy it is to add a new LLM provider
without changing any existing code - just following the interface.
"""

import asyncio
import json
from typing import Any, Dict, List

from app.services.llm_service import LLMServiceInterface

from app.config import get_settings
from app.models import BankStatement, Transaction


class LocalLlamaService(LLMServiceInterface):
    """
    Example implementation for a local Llama model

    This shows how ANY LLM can be added as a drop-in replacement
    by implementing the LLMServiceInterface
    """

    def __init__(self):
        self.settings = get_settings()
        # In a real implementation, you'd initialize your local model here
        # self.model = load_local_llama_model()
        # self.tokenizer = load_tokenizer()

    async def parse_text_statement(self, text_content: str) -> BankStatement:
        """Parse bank statement from text using Local Llama"""
        try:
            # In a real implementation, you'd call your local model
            prompt = self._get_parsing_prompt()
            full_prompt = f"{prompt}\n\nBank Statement Text:\n{text_content}"

            # Simulate local model call
            # response = await self._call_local_model(full_prompt)

            # For demo purposes, return a mock response
            mock_response = self._get_mock_response()

            # Parse and validate the response
            return self._convert_to_bank_statement(mock_response)

        except Exception as e:
            raise Exception(f"Failed to parse statement with Local Llama: {str(e)}")

    async def parse_image_statement(self, base64_images: List[str]) -> BankStatement:
        """Parse bank statement from images using Local Llama (if vision-capable)"""
        try:
            # For vision-capable local models like LLaVA
            # prompt = self._get_parsing_prompt()
            # response = await self._call_local_vision_model(prompt, base64_images)

            # For demo, fall back to text extraction then processing
            # In reality, you'd either:
            # 1. Use a vision-capable local model
            # 2. Raise NotImplementedError if no vision support

            raise NotImplementedError(
                "Local Llama vision processing not implemented in this demo"
            )

        except Exception as e:
            raise Exception(f"Failed to parse images with Local Llama: {str(e)}")

    def _get_parsing_prompt(self) -> str:
        """Get the parsing prompt - same as other implementations"""
        return """
        You are a bank statement parsing expert. Extract and standardize the following bank statement data into JSON format.

        Required fields:
        - account_holder: Full name of the account holder
        - bank_name: Name of the bank
        - account_number: Account number (mask with *)
        - statement_period: Object with start_date and end_date (YYYY-MM-DD)
        - opening_balance: Starting balance as number
        - closing_balance: Ending balance as number
        - transactions: Array of transaction objects
        - currency: Currency code (default USD)

        For each transaction:
        - date: Transaction date (YYYY-MM-DD)
        - description: Transaction description
        - amount: Transaction amount (positive number)
        - type: "credit" or "debit"
        - category: Transaction category (optional)

        Return ONLY valid JSON without markdown formatting.
        """

    async def _call_local_model(self, prompt: str) -> str:
        """Call the local Llama model"""
        # In a real implementation:
        # 1. Tokenize the prompt
        # 2. Generate response using your local model
        # 3. Decode the response
        # 4. Return the generated text

        # Example pseudo-code:
        # inputs = self.tokenizer(prompt, return_tensors="pt")
        # outputs = self.model.generate(**inputs, max_length=2048)
        # response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # return response[len(prompt):].strip()

        # For demo, simulate processing time
        await asyncio.sleep(0.1)
        return json.dumps(self._get_mock_response())

    def _get_mock_response(self) -> Dict[str, Any]:
        """Mock response for demonstration"""
        return {
            "account_holder": "Jane Smith",
            "bank_name": "Local Credit Union",
            "account_number": "****5678",
            "statement_period": {"start_date": "2024-01-01", "end_date": "2024-01-31"},
            "opening_balance": 1500.00,
            "closing_balance": 1750.00,
            "transactions": [
                {
                    "date": "2024-01-15",
                    "description": "Salary Deposit",
                    "amount": 2500.00,
                    "type": "credit",
                    "category": "income",
                },
                {
                    "date": "2024-01-20",
                    "description": "Grocery Store",
                    "amount": 125.50,
                    "type": "debit",
                    "category": "food",
                },
            ],
            "currency": "USD",
        }

    def _convert_to_bank_statement(self, data: Dict[str, Any]) -> BankStatement:
        """Convert parsed data to BankStatement model - same as other implementations"""
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
                    balance=float(txn_data["balance"])
                    if txn_data.get("balance")
                    else None,
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
                currency=data.get("currency", "USD"),
            )

            return bank_statement

        except Exception as e:
            raise Exception(f"Failed to convert data to BankStatement model: {str(e)}")


# Example of how to integrate the new LLM into the factory
def add_local_llama_to_factory():
    """
    Example showing how to extend the LLMServiceFactory

    You would add this method to the existing LLMServiceFactory class:
    """

    # Add new method to factory (in practice, you'd modify the class directly)
    @staticmethod
    def create_local_llama_service():
        """Create Local Llama service"""
        return LocalLlamaService()


# Example usage in parser factory
def add_local_llama_parser():
    """
    Example showing how to add Local Llama to BankStatementParserFactory

    You would add this method to the existing BankStatementParserFactory class:
    """
    from app.services.pdf_processor import PDFProcessorFactory

    @staticmethod
    def create_local_llama_parser():
        """Create parser with Local Llama LLM"""
        from app.services.parser_service import BankStatementParserService

        return BankStatementParserService(
            pdf_processor=PDFProcessorFactory.create_image_processor(),
            llm_service=LocalLlamaService(),  # Drop-in replacement!
        )


# Example usage
async def demo_local_llama():
    """Demo the Local Llama service"""

    # Create the service
    llama_service = LocalLlamaService()

    # Mock bank statement text
    mock_text = """
    CHASE BANK
    Account Statement
    
    Account Holder: John Doe
    Account Number: 1234567890
    Statement Period: January 1, 2024 - January 31, 2024
    
    Opening Balance: $2,500.00
    
    Transactions:
    01/05/2024  Direct Deposit - Salary        +$3,000.00
    01/10/2024  Grocery Store                  -$125.50
    01/15/2024  Gas Station                    -$45.00
    
    Closing Balance: $5,329.50
    """

    # Parse the statement
    try:
        result = await llama_service.parse_text_statement(mock_text)
        print("✅ Local Llama parsing successful!")
        print(f"Account Holder: {result.account_holder}")
        print(f"Bank: {result.bank_name}")
        print(f"Transactions: {len(result.transactions)}")
        return result
    except Exception as e:
        print(f"❌ Local Llama parsing failed: {e}")
        return None


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_local_llama())
