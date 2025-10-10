"""
Claude (Anthropic) service implementation
"""

from typing import List, Dict, Any
# import anthropic  # Uncomment when adding Claude dependency
from app.models import BankStatement
from .interface import LLMServiceInterface
from .openai_service import OpenAIService  # For reusing prompt


class ClaudeService(LLMServiceInterface):
    """Claude (Anthropic) service implementation"""
    
    def __init__(self):
        # self.settings = get_settings()
        # self.client = anthropic.Anthropic(api_key=self.settings.claude_api_key)
        pass
    
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
            raise NotImplementedError(
                "Claude implementation pending. "
                "To implement:\n"
                "1. Add 'anthropic' to requirements.txt\n"
                "2. Add CLAUDE_API_KEY to .env\n"
                "3. Uncomment and complete the implementation above"
            )
            
        except NotImplementedError:
            raise
        except Exception as e:
            raise Exception(f"Failed to parse statement with Claude: {str(e)}")
    
    async def parse_image_statement(self, base64_images: List[str]) -> BankStatement:
        """Parse bank statement from images using Claude"""
        # Claude 3 supports vision
        raise NotImplementedError(
            "Claude vision implementation pending. "
            "Claude 3 supports vision - implement similar to OpenAI vision"
        )
    
    def _get_parsing_prompt(self) -> str:
        """Reuse the same prompt as OpenAI for consistency"""
        return OpenAIService()._get_parsing_prompt()