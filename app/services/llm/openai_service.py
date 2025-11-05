"""
OpenAI GPT service implementation
"""

import logging
from typing import Any, Dict, List

import openai

from app.config import get_settings

from .base import BaseLLMService

# Configure logging
logger = logging.getLogger(__name__)


class OpenAIService(BaseLLMService):
    """OpenAI GPT service implementation (Single Responsibility Principle)"""

    def __init__(self):
        self.settings = get_settings()
        openai.api_key = self.settings.openai_api_key
        self.client = openai.OpenAI(api_key=self.settings.openai_api_key)

    def _is_gpt5_family(self, model_name: str) -> bool:
        return "gpt-5" in model_name.lower()

    def _get_provider_specific_instructions(self) -> str:
        """OpenAI-specific parsing instructions for enhanced accuracy"""
        return """
OPENAI-SPECIFIC REQUIREMENTS:
⚠️ CRITICAL: It is absolutely critical that you extract all details properly and accurately.
- Do NOT skip any transactions
- Do NOT reorder transactions
- Do NOT guess values - extract what you see
- Maintain the exact sequence as it appears in the statement

ACCURACY EMPHASIS:
Your parsing accuracy directly impacts financial record keeping. Every transaction matters.
Double-check your extraction before returning the result.
""".strip()

    # Base prompt and JSON utilities are inherited from BaseLLMService

    async def _single_text_call(
        self, text_content: str, next_page_hint: str | None
    ) -> Dict[str, Any]:
        model_name = self.settings.llm_model_name.replace("-vision-preview", "")

        if self._is_gpt5_family(model_name):
            # GPT-5 uses the Responses API with different structure
            system_prompt = self._get_parsing_prompt()
            user_prompt = (
                f"Parse this bank statement:\n\n{text_content}"
                if not next_page_hint
                else f"Continue parsing this bank statement starting from: {next_page_hint}\n\n{text_content}"
            )
            # Combine system and user prompts
            combined_input = f"{system_prompt}\n\n{user_prompt}"

            response = self.client.responses.create(
                model=model_name,
                input=[{"type": "message", "role": "user", "content": combined_input}],
                reasoning={"effort": self.settings.gpt5_reasoning_effort},
                text={"verbosity": self.settings.gpt5_text_verbosity},
                max_output_tokens=self.settings.max_tokens,
            )
            # Extract text from output items - GPT-5 returns ResponseOutputMessage with nested content
            json_content = ""
            for item in response.output:
                # Skip reasoning items
                if hasattr(item, "type") and item.type == "reasoning":
                    continue

                # Check for message type with content array
                if hasattr(item, "type") and item.type == "message":
                    if hasattr(item, "content") and isinstance(item.content, list):
                        for content_item in item.content:
                            # Look for output_text type
                            if (
                                hasattr(content_item, "type")
                                and content_item.type == "output_text"
                            ):
                                if hasattr(content_item, "text") and content_item.text:
                                    json_content = content_item.text
                                    break
                        if json_content:
                            break

                # Fallback: check for direct content attribute (older format)
                if hasattr(item, "content") and isinstance(item.content, str):
                    json_content = item.content
                    break

            if not json_content:
                raise ValueError(
                    f"No text content in response. Status: {
                        response.status
                    }, Output items: {
                        [item.type for item in response.output if hasattr(item, 'type')]
                    }"
                )

            logger.debug(
                f"GPT-5 text parsing - Extracted {
                    len(json_content)
                } characters from text content, "
                f"Preview: {json_content[:150]}..."
            )

            parsed_data = self._parse_response_json(json_content.strip())
            return parsed_data

        # Chat Completions API for non-GPT-5 models
        kwargs: Dict[str, Any] = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": self._get_parsing_prompt()},
                {
                    "role": "user",
                    "content": (
                        f"Parse this bank statement:\n\n{text_content}"
                        if not next_page_hint
                        else f"Continue parsing this bank statement starting from: {next_page_hint}\n\n{text_content}"
                    ),
                },
            ],
            "temperature": self.settings.temperature,
        }
        if self._is_json_mode_supported(model_name):
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        json_content = response.choices[0].message.content or ""

        # Log the text completion response
        logger.debug(
            f"GPT-4 text API response - "
            f"Model: {response.model}, "
            f"Finish reason: {response.choices[0].finish_reason}, "
            f"Tokens used: {
                response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'
            }, "
            f"Content length: {len(json_content)} chars, "
            f"Preview: {json_content[:150]}..."
        )

        parsed_data = self._parse_response_json(json_content.strip())
        return parsed_data

    async def _single_image_call(
        self, base64_images: List[str], next_page_hint: str | None
    ) -> Dict[str, Any]:
        model_name = self.settings.llm_model_name

        if self._is_gpt5_family(model_name):
            # GPT-5 uses the Responses API with image support
            system_prompt = self._get_parsing_prompt()
            text_prompt = (
                "Parse this bank statement from the provided images:"
                if not next_page_hint
                else f"Continue parsing this bank statement starting from: {next_page_hint}"
            )

            # Build content array with images first, then text (per best practices)
            content_parts = []
            for base64_image in base64_images:
                content_parts.append(
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{base64_image}",
                        "detail": "auto",
                    }
                )
            # Add text after images for better results
            content_parts.append(
                {"type": "input_text", "text": f"{system_prompt}\n\n{text_prompt}"}
            )

            response = self.client.responses.create(
                model=model_name,
                input=[{"role": "user", "content": content_parts}],
                reasoning={"effort": self.settings.gpt5_reasoning_effort},
                text={"verbosity": self.settings.gpt5_text_verbosity},
                max_output_tokens=self.settings.max_tokens,
            )

            # Log the full response for debugging GPT-5 vision calls
            logger.debug(
                f"GPT-5 vision API response - Status: {response.status}, "
                f"Model: {model_name}, "
                f"Images processed: {len(base64_images)}, "
                f"Output types: {
                    [item.type for item in response.output if hasattr(item, 'type')]
                }"
            )

            # Extract text from output items - GPT-5 returns ResponseOutputMessage with nested content
            json_content = ""
            for item in response.output:
                # Skip reasoning items
                if hasattr(item, "type") and item.type == "reasoning":
                    continue

                # Check for message type with content array
                if hasattr(item, "type") and item.type == "message":
                    if hasattr(item, "content") and isinstance(item.content, list):
                        for content_item in item.content:
                            # Look for output_text type
                            if (
                                hasattr(content_item, "type")
                                and content_item.type == "output_text"
                            ):
                                if hasattr(content_item, "text") and content_item.text:
                                    json_content = content_item.text
                                    break
                        if json_content:
                            break

                # Fallback: check for direct content attribute (older format)
                if hasattr(item, "content") and isinstance(item.content, str):
                    json_content = item.content
                    break

            if not json_content:
                raise ValueError(
                    f"No text content in response. Status: {
                        response.status
                    }, Output items: {
                        [item.type for item in response.output if hasattr(item, 'type')]
                    }"
                )

            logger.debug(
                f"GPT-5 vision parsing - Extracted {
                    len(json_content)
                } characters from vision response, "
                f"Preview: {json_content[:150]}..."
            )

            parsed_data = self._parse_response_json(json_content.strip())
            return parsed_data

        # Chat Completions API for non-GPT-5 models
        messages = [{"role": "system", "content": self._get_parsing_prompt()}]
        user_content: List[Dict[str, Any]] = [
            {
                "type": "text",
                "text": (
                    "Parse this bank statement from the provided images:"
                    if not next_page_hint
                    else f"Continue parsing this bank statement starting from: {next_page_hint}"
                ),
            }
        ]
        for base64_image in base64_images:
            user_content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                }
            )
        messages.append({"role": "user", "content": user_content})

        kwargs: Dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "temperature": self.settings.temperature,
        }
        if self._is_json_mode_supported(model_name):
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)

        # Log the completion response for debugging
        json_content = response.choices[0].message.content or ""
        logger.debug(
            f"GPT-4 vision API response - "
            f"Model: {response.model}, "
            f"Images: {len(base64_images)}, "
            f"Finish reason: {response.choices[0].finish_reason}, "
            f"Tokens used: {
                response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'
            }, "
            f"Content preview: {json_content[:200]}..."
        )

        parsed_data = self._parse_response_json(json_content.strip())
        return parsed_data

    # Conversion to BankStatement is inherited from BaseLLMService
