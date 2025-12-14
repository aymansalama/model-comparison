"""Base provider client interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class ModelResponse:
    """Standardized model response."""

    text: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    latency_ms: Optional[float] = None
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class ProviderClient(ABC):
    """Abstract base class for provider clients."""

    @abstractmethod
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
        """
        Generate text from a prompt.

        Args:
            prompt: Input prompt
            model_id: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            timeout: Request timeout in seconds
            **kwargs: Additional provider-specific parameters

        Returns:
            ModelResponse with generated text and metadata
        """
        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate provider credentials.

        Returns:
            True if credentials are valid
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """
        Get list of available model IDs.

        Returns:
            List of model identifiers
        """
        pass
