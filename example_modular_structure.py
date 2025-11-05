"""
Example: Adding a new LLM provider with the separated file structure

This demonstrates how the new modular structure makes it even easier
to add new LLM providers - each in its own dedicated file.
"""

import asyncio
from typing import Any, Dict, List

from app.models import BankStatement, Transaction
from app.services.llm.interface import LLMServiceInterface
from app.services.llm.openai_service import OpenAIService


class LocalLlamaService(LLMServiceInterface):
    """
    Example: Local Llama implementation in its own file

    File location: app/services/llm/local_llama_service.py
    """

    def __init__(self):
        # In real implementation:
        # import ollama
        # self.client = ollama.Client()
        pass

    async def parse_text_statement(self, text_content: str) -> BankStatement:
        """Parse bank statement from text using Local Llama"""
        try:
            # Real implementation would be:
            # response = self.client.generate(
            #     model='llama2',
            #     prompt=f"{self._get_parsing_prompt()}\n\n{text_content}"
            # )
            # json_content = response['response']

            # For demo, return mock data
            mock_response = self._get_mock_response()
            return self._convert_to_bank_statement(mock_response)

        except Exception as e:
            raise Exception(f"Failed to parse statement with Local Llama: {str(e)}")

    async def parse_image_statement(self, base64_images: List[str]) -> BankStatement:
        """Parse bank statement from images using Local Llama + LLaVA"""
        # Real implementation with LLaVA:
        # response = self.client.generate(
        #     model='llava',
        #     prompt=self._get_parsing_prompt(),
        #     images=base64_images
        # )

        raise NotImplementedError("Local Llama vision not implemented in demo")

    def _get_parsing_prompt(self) -> str:
        """Reuse OpenAI prompt for consistency"""
        return OpenAIService()._get_parsing_prompt()

    def _get_mock_response(self) -> Dict[str, Any]:
        """Mock response for demo"""
        return {
            "account_holder": "Local User",
            "bank_name": "Community Bank",
            "account_number": "****9999",
            "statement_period": {"start_date": "2024-01-01", "end_date": "2024-01-31"},
            "opening_balance": 1000.00,
            "closing_balance": 1200.00,
            "transactions": [
                {
                    "date": "2024-01-15",
                    "description": "Local Llama Salary",
                    "amount": 2000.00,
                    "type": "credit",
                    "category": "income",
                }
            ],
            "currency": "USD",
        }

    def _convert_to_bank_statement(self, data: Dict[str, Any]) -> BankStatement:
        """Convert to BankStatement model - same logic as OpenAI"""
        transactions = []
        for txn_data in data.get("transactions", []):
            transaction = Transaction(
                date=txn_data["date"],
                description=txn_data["description"],
                amount=float(txn_data["amount"]),
                type=txn_data["type"],
                category=txn_data.get("category"),
            )
            transactions.append(transaction)

        return BankStatement(
            account_holder=data["account_holder"],
            bank_name=data["bank_name"],
            account_number=data["account_number"],
            statement_period=data["statement_period"],
            opening_balance=float(data["opening_balance"]),
            closing_balance=float(data["closing_balance"]),
            transactions=transactions,
            currency=data.get("currency", "USD"),
        )


# To integrate this new LLM, you would:

# 1. Save this class in: app/services/llm/local_llama_service.py


# 2. Add to factory (app/services/llm/factory.py):
def add_to_factory():
    """
    Add this import and method to LLMServiceFactory:

    from .local_llama_service import LocalLlamaService

    @staticmethod
    def create_local_llama_service() -> LLMServiceInterface:
        return LocalLlamaService()
    """
    pass


# 3. Add to parser factory (app/services/parser_service.py):
def add_to_parser_factory():
    """
    Add this method to BankStatementParserFactory:

    @staticmethod
    def create_local_llama_parser() -> BankStatementParserService:
        return BankStatementParserService(
            llm_service=LLMServiceFactory.create_local_llama_service()
        )
    """
    pass


# 4. Optionally add to API enum (app/api/routes.py):
def add_to_api():
    """
    Add to LLMProvider enum:

    class LLMProvider(str, Enum):
        openai = "openai"
        claude = "claude"
        gemini = "gemini"
        local_llama = "local_llama"  # Add this

    Update get_parser_service function:

    elif llm_provider == LLMProvider.local_llama:
        return BankStatementParserFactory.create_local_llama_parser()
    """
    pass


# That's it! No other files need to change.


async def demo_new_structure():
    """Demo the new modular structure"""
    print("🏗️  New Modular Structure Demo")
    print("=" * 50)

    # Each LLM is now in its own file:
    print("📁 LLM Services:")
    print("   ├── interface.py        (contract)")
    print("   ├── openai_service.py   (OpenAI implementation)")
    print("   ├── claude_service.py   (Claude implementation)")
    print("   ├── gemini_service.py   (Gemini implementation)")
    print("   ├── local_llama_service.py (Your custom LLM)")
    print("   └── factory.py          (creates any LLM)")

    print("\n📁 PDF Services:")
    print("   ├── interface.py        (contract)")
    print("   ├── text_extractor.py   (text processing)")
    print("   ├── image_extractor.py  (image processing)")
    print("   └── factory.py          (creates processors)")

    print("\n📁 Validation Services:")
    print("   ├── interface.py        (contract)")
    print("   ├── pdf_validator.py    (PDF validation)")
    print("   ├── validation_service.py (orchestrator)")
    print("   └── factory.py          (creates validators)")

    print("\n🎯 Benefits:")
    print("   ✅ Each implementation in its own file")
    print("   ✅ Easy to find and modify specific LLMs")
    print("   ✅ Clear separation of concerns")
    print("   ✅ Easy to add new implementations")
    print("   ✅ Better code organization")
    print("   ✅ Easier testing and maintenance")

    # Demo the service
    llama_service = LocalLlamaService()
    result = await llama_service.parse_text_statement("Mock bank statement")

    print("Local Llama Demo Result")
    print(f"   Account: {result.account_holder}")
    print(f"   Bank: {result.bank_name}")
    print(f"   Transactions: {len(result.transactions)}")


if __name__ == "__main__":
    asyncio.run(demo_new_structure())
    asyncio.run(demo_new_structure())
