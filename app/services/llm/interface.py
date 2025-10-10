from abc import ABC, abstractmethod
from typing import List
from app.models import BankStatement


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