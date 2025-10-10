"""
OpenAI GPT service implementation
"""

from typing import List, Dict, Any
import openai
import json
from app.models import BankStatement
from app.config import get_settings
from .base import BaseLLMService


class OpenAIService(BaseLLMService):
    """OpenAI GPT service implementation (Single Responsibility Principle)"""
    
    def __init__(self):
        self.settings = get_settings()
        openai.api_key = self.settings.openai_api_key
        self.client = openai.OpenAI(api_key=self.settings.openai_api_key)
    
    def _is_gpt5_family(self, model_name: str) -> bool:
        return "gpt-5" in model_name.lower()
    
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
        - currency: Currency code (default USD)

        For each transaction, include:
        - date: Transaction date (YYYY-MM-DD format)
        - description: Transaction description
        - amount: Transaction amount (positive number)
        - type: "credit" or "debit"
        - category: Transaction category (optional)
        - balance: Running balance after transaction (optional)

        Return ONLY valid JSON (no markdown code fences, no comments, no explanations), do not use "\n" in the JSON.
        Do not include trailing commas. Use numbers, not strings, for amounts/balances.
        If there is a page that is sent and does not look like a statement, example(detail pages, contact information pages, etc.) from the bank, do not send false data, just send transactions as [].
        Pay attention to the type of the transaction, there are banks (not all of them) that end their number in CR or DB it means credit or debit respectively. example: 10000CR means 10000 credit.
        Schema:
        {
            "account_holder": string,
            "bank_name": string,
            "account_number": string,  // last 4 visible, others masked with *
            "statement_period": { "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" },
            "opening_balance": number,
            "closing_balance": number,
            "transactions": [
                { "date": "YYYY-MM-DD", "description": string, "amount": number, "type": "credit"|"debit", "category": string? }
            ],
            "currency": "USD",
            "has_more": boolean,
            "next_page_hint": string?
        }
        Output the JSON object only.
        After extraction ensure that for all transactions balance matches the previous transaction + deposited or withdrawn amount in that transaction, also validate your extraction by checking opening and closing balance. It is absolutely critical that you extract all details properly and do not reorder or skip a transaction or you will loose your job
        """
    
    # JSON utilities and prompt helpers are inherited from BaseLLMService

    async def _single_text_call(self, text_content: str, next_page_hint: str | None) -> Dict[str, Any]:
        model_name = self.settings.llm_model_name.replace("-vision-preview", "")
        kwargs: Dict[str, Any] = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": self._get_parsing_prompt()},
                {"role": "user", "content": (
                    f"Parse this bank statement:\n\n{text_content}" if not next_page_hint else
                    f"Continue parsing this bank statement starting from: {next_page_hint}\n\n{text_content}"
                )}
            ],
            "temperature": self.settings.temperature,
        }
        if self._is_gpt5_family(model_name):
            kwargs["reasoning_effort"] = "low"
            if self.settings.max_tokens:
                kwargs["max_completion_tokens"] = self.settings.max_tokens
        if self._is_json_mode_supported(model_name):
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        json_content = response.choices[0].message.content or ""
        parsed_data = self._parse_response_json(json_content.strip())
        return parsed_data
    
    async def _single_image_call(self, base64_images: List[str], next_page_hint: str | None) -> Dict[str, Any]:
        # Prepare messages with images
        messages = [
            {"role": "system", "content": self._get_parsing_prompt()}
        ]
        user_content: List[Dict[str, Any]] = [
            {"type": "text", "text": (
                "Parse this bank statement from the provided images:" if not next_page_hint else
                f"Continue parsing this bank statement starting from: {next_page_hint}"
            )}
        ]
        for base64_image in base64_images:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
            })
        messages.append({"role": "user", "content": user_content})

        model_name = self.settings.llm_model_name
        kwargs: Dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "temperature": self.settings.temperature,
        }
        if self._is_gpt5_family(model_name):
            kwargs["reasoning_effort"] = "low"
            if self.settings.max_tokens:
                kwargs["max_completion_tokens"] = self.settings.max_tokens
        if self._is_json_mode_supported(model_name):
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        print(response)
        print(response.choices[0].message.content)
        json_content = response.choices[0].message.content or ""
        parsed_data = self._parse_response_json(json_content.strip())
        return parsed_data
    
    # Conversion to BankStatement is inherited from BaseLLMService