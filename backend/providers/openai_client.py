"""OpenAI provider client."""
import time
from typing import Optional
from openai import AsyncOpenAI, OpenAIError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from .base import ProviderClient, ModelResponse
from config import settings


class OpenAIClient(ProviderClient):
    """OpenAI API client."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key (uses settings if not provided)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        self.client = AsyncOpenAI(api_key=self.api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((OpenAIError,)),
    )
    async def generate(
        self,
        prompt: str,
        model_id: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
        top_p: float = 1.0,
        timeout: int = 60,
        **kwargs,
    ) -> ModelResponse:
        """Generate text using OpenAI API."""
        start_time = time.time()

        try:
            response = await self.client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                timeout=timeout,
                **kwargs,
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract response text
            text = response.choices[0].message.content or ""

            # Extract token usage
            input_tokens = response.usage.prompt_tokens if response.usage else None
            output_tokens = response.usage.completion_tokens if response.usage else None

            return ModelResponse(
                text=text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                finish_reason=response.choices[0].finish_reason,
                raw_response=response.model_dump() if hasattr(response, "model_dump") else None,
            )

        except OpenAIError as e:
            # Re-raise for retry mechanism
            raise
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    async def validate_credentials(self) -> bool:
        """Validate OpenAI API credentials."""
        try:
            # Try to list models as a credential check
            await self.client.models.list()
            return True
        except Exception:
            return False

    def get_available_models(self) -> list[str]:
        """Get available OpenAI models."""
        return [
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-4-0613",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0125",
        ]
