"""
Claude (Anthropic) service implementation
"""

from typing import List, Dict, Any
# import anthropic  # Uncomment when adding Claude dependency
# from app.config import get_settings  # Uncomment when adding Claude
from .base import BaseLLMService


class ClaudeService(BaseLLMService):
    """Claude (Anthropic) service implementation"""

    def __init__(self):
        # self.settings = get_settings()
        # self.client = anthropic.Anthropic(api_key=self.settings.claude_api_key)
        pass

    def _get_provider_specific_instructions(self) -> str:
        """Claude-specific parsing instructions leveraging reasoning capabilities"""
        return """
CLAUDE-SPECIFIC GUIDANCE:
- Use your strong reasoning capabilities to handle ambiguous cases
- If uncertain about a value, provide your best inference based on context
- Pay special attention to date formats - verify year/month/day order
- For complex table layouts, parse systematically row by row
- Use chain-of-thought reasoning for validation checks

Claude: Your strength is careful, methodical analysis. Use it to ensure accuracy.
""".strip()

    async def _single_text_call(self, text_content: str, next_page_hint: str | None) -> Dict[str, Any]:
        """Perform single text-only Claude API call and return parsed JSON as dict"""
        # Example Claude implementation:
        # response = self.client.messages.create(
        #     model="claude-3-opus-20240229",
        #     max_tokens=4000,
        #     messages=[
        #         {"role": "user", "content": (
        #             f"{self._get_parsing_prompt()}\n\nParse this bank statement:\n\n{text_content}"
        #             if not next_page_hint else
        #             f"{self._get_parsing_prompt()}\n\nContinue from: {next_page_hint}\n\n{text_content}"
        #         )}
        #     ]
        # )
        # json_content = response.content[0].text
        # return self._parse_response_json(json_content)

        raise NotImplementedError(
            "Claude implementation pending. "
            "To implement:\n"
            "1. Add 'anthropic' to requirements.txt\n"
            "2. Add CLAUDE_API_KEY to .env\n"
            "3. Uncomment and complete the implementation above"
        )

    async def _single_image_call(self, base64_images: List[str], next_page_hint: str | None) -> Dict[str, Any]:
        """Perform single vision Claude API call and return parsed JSON as dict"""
        # Example Claude Vision implementation:
        # content = []
        # for base64_image in base64_images:
        #     content.append({
        #         "type": "image",
        #         "source": {
        #             "type": "base64",
        #             "media_type": "image/png",
        #             "data": base64_image,
        #         }
        #     })
        # content.append({
        #     "type": "text",
        #     "text": (
        #         f"{self._get_parsing_prompt()}\n\nParse this bank statement from the images:"
        #         if not next_page_hint else
        #         f"{self._get_parsing_prompt()}\n\nContinue from: {next_page_hint}"
        #     )
        # })
        #
        # response = self.client.messages.create(
        #     model="claude-3-opus-20240229",
        #     max_tokens=4000,
        #     messages=[{"role": "user", "content": content}]
        # )
        # json_content = response.content[0].text
        # return self._parse_response_json(json_content)

        raise NotImplementedError(
            "Claude vision implementation pending. "
            "Claude 3 supports vision - implement similar to OpenAI vision"
        )

    # Inherits parse_text_statement(), parse_image_statement(), and all JSON helpers from BaseLLMService