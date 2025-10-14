"""
Google Gemini service implementation
"""

from typing import List, Dict, Any
# import google.generativeai as genai  # Uncomment when adding Gemini
# from app.config import get_settings  # Uncomment when adding Gemini
from .base import BaseLLMService


class GeminiService(BaseLLMService):
    """Google Gemini service implementation"""

    def __init__(self):
        # self.settings = get_settings()
        # genai.configure(api_key=self.settings.gemini_api_key)
        # self.text_model = genai.GenerativeModel('gemini-pro')
        # self.vision_model = genai.GenerativeModel('gemini-pro-vision')
        pass

    def _get_provider_specific_instructions(self) -> str:
        """Gemini-specific parsing instructions leveraging multimodal capabilities"""
        return """
GEMINI-SPECIFIC GUIDANCE:
- Leverage your multimodal capabilities for complex PDF layouts
- Use visual context to understand table structures and formatting
- Extract amounts even from non-standard formats (with commas, currency symbols, etc.)
- Pay attention to both textual and spatial relationships in the document
- Use your broad context window to understand document structure

Gemini: Your multimodal vision excels at complex document layouts. Use this strength.
""".strip()

    async def _single_text_call(self, text_content: str, next_page_hint: str | None) -> Dict[str, Any]:
        """Perform single text-only Gemini API call and return parsed JSON as dict"""
        # Example Gemini implementation:
        # model = genai.GenerativeModel('gemini-pro')
        # prompt = (
        #     f"{self._get_parsing_prompt()}\n\nParse this bank statement:\n\n{text_content}"
        #     if not next_page_hint else
        #     f"{self._get_parsing_prompt()}\n\nContinue from: {next_page_hint}\n\n{text_content}"
        # )
        # response = model.generate_content(prompt)
        # json_content = response.text
        # return self._parse_response_json(json_content)

        raise NotImplementedError(
            "Gemini implementation pending. "
            "To implement:\n"
            "1. Add 'google-generativeai' to requirements.txt\n"
            "2. Add GEMINI_API_KEY to .env\n"
            "3. Uncomment and complete the implementation above"
        )

    async def _single_image_call(self, base64_images: List[str], next_page_hint: str | None) -> Dict[str, Any]:
        """Perform single vision Gemini API call and return parsed JSON as dict"""
        # Example Gemini Vision implementation:
        # import PIL.Image
        # import io
        # import base64
        #
        # images = []
        # for b64_image in base64_images:
        #     image_data = base64.b64decode(b64_image)
        #     image = PIL.Image.open(io.BytesIO(image_data))
        #     images.append(image)
        #
        # prompt = (
        #     f"{self._get_parsing_prompt()}\n\nParse this bank statement from the images:"
        #     if not next_page_hint else
        #     f"{self._get_parsing_prompt()}\n\nContinue from: {next_page_hint}"
        # )
        #
        # model = genai.GenerativeModel('gemini-pro-vision')
        # response = model.generate_content([prompt, *images])
        # json_content = response.text
        # return self._parse_response_json(json_content)

        raise NotImplementedError(
            "Gemini vision implementation pending. "
            "Gemini Pro Vision supports image analysis"
        )

    # Inherits parse_text_statement(), parse_image_statement(), and all JSON helpers from BaseLLMService