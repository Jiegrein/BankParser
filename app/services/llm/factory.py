"""
LLM Service Factory for creating different LLM service instances
"""

from .claude_service import ClaudeService
from .gemini_service import GeminiService
from .interface import LLMServiceInterface
from .openai_service import OpenAIService


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


# Convenience exports
__all__ = [
    "LLMServiceInterface",
    "LLMServiceFactory",
    "OpenAIService",
    "ClaudeService",
    "GeminiService",
]
