"""
Google Gemini service implementation
"""

from typing import List
# import google.generativeai as genai  # Uncomment when adding Gemini
from app.models import BankStatement
from .base import BaseLLMService


class GeminiService(BaseLLMService):
    """Google Gemini service implementation"""
    
    def __init__(self):
        # self.settings = get_settings()
        # genai.configure(api_key=self.settings.gemini_api_key)
        # self.model = genai.GenerativeModel('gemini-pro-vision')
        pass
    
    async def parse_text_statement(self, text_content: str) -> BankStatement:
        """Parse bank statement from text using Gemini"""
        # Example Gemini implementation
        # model = genai.GenerativeModel('gemini-pro')
        # response = model.generate_content([
        #     self._get_parsing_prompt(),
        #     text_content
        # ])
        # json_content = response.text
        
        raise NotImplementedError(
            "Gemini implementation pending. "
            "To implement:\n"
            "1. Add 'google-generativeai' to requirements.txt\n"
            "2. Add GEMINI_API_KEY to .env\n"
            "3. Uncomment and complete the implementation above"
        )
    
    async def parse_image_statement(self, base64_images: List[str]) -> BankStatement:
        """Parse bank statement from images using Gemini"""
        # Example Gemini Vision implementation
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
        # model = genai.GenerativeModel('gemini-pro-vision')
        # response = model.generate_content([
        #     self._get_parsing_prompt(),
        #     *images
        # ])
        
        raise NotImplementedError(
            "Gemini vision implementation pending. "
            "Gemini Pro Vision supports image analysis"
        )
    
    # Inherits shared _get_parsing_prompt and JSON helpers from BaseLLMService