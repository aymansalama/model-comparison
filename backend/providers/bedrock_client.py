"""Amazon Bedrock provider client."""
import time
import json
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from .base import ProviderClient, ModelResponse
from config import settings


class BedrockClient(ProviderClient):
    """Amazon Bedrock API client."""

    def __init__(
        self,
        region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        """
        Initialize Bedrock client.

        Args:
            region: AWS region
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
        """
        self.region = region or settings.AWS_REGION

        # Configure boto3 session
        session_kwargs = {"region_name": self.region}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs["aws_access_key_id"] = aws_access_key_id
            session_kwargs["aws_secret_access_key"] = aws_secret_access_key

        session = boto3.Session(**session_kwargs)
        self.client = session.client("bedrock-runtime")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ClientError, BotoCoreError)),
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
        """Generate text using Bedrock API."""
        start_time = time.time()

        try:
            # Prepare request body based on model family
            body = self._prepare_request_body(
                prompt, model_id, temperature, max_tokens, top_p, **kwargs
            )

            # Invoke model
            response = self.client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )

            latency_ms = (time.time() - start_time) * 1000

            # Parse response
            response_body = json.loads(response["body"].read())
            parsed = self._parse_response(response_body, model_id)

            return ModelResponse(
                text=parsed["text"],
                input_tokens=parsed.get("input_tokens"),
                output_tokens=parsed.get("output_tokens"),
                latency_ms=latency_ms,
                finish_reason=parsed.get("finish_reason"),
                raw_response=response_body,
            )

        except (ClientError, BotoCoreError) as e:
            raise
        except Exception as e:
            raise RuntimeError(f"Bedrock API error: {str(e)}")

    def _prepare_request_body(
        self,
        prompt: str,
        model_id: str,
        temperature: float,
        max_tokens: int,
        top_p: float,
        **kwargs,
    ) -> Dict[str, Any]:
        """Prepare request body based on model family."""
        if "claude" in model_id.lower():
            # Anthropic Claude models
            return {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
            }
        elif "titan" in model_id.lower():
            # Amazon Titan models
            return {
                "inputText": prompt,
                "textGenerationConfig": {
                    "temperature": temperature,
                    "maxTokenCount": max_tokens,
                    "topP": top_p,
                },
            }
        elif "mistral" in model_id.lower() or "mixtral" in model_id.lower():
            # Mistral models
            return {
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
            }
        else:
            # Generic format (try Claude format)
            return {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
            }

    def _parse_response(
        self, response_body: Dict[str, Any], model_id: str
    ) -> Dict[str, Any]:
        """Parse response based on model family."""
        if "claude" in model_id.lower():
            # Anthropic Claude models
            content = response_body.get("content", [])
            text = content[0].get("text", "") if content else ""
            usage = response_body.get("usage", {})

            return {
                "text": text,
                "input_tokens": usage.get("input_tokens"),
                "output_tokens": usage.get("output_tokens"),
                "finish_reason": response_body.get("stop_reason"),
            }
        elif "titan" in model_id.lower():
            # Amazon Titan models
            results = response_body.get("results", [])
            text = results[0].get("outputText", "") if results else ""

            return {
                "text": text,
                "input_tokens": response_body.get("inputTextTokenCount"),
                "output_tokens": results[0].get("tokenCount") if results else None,
                "finish_reason": results[0].get("completionReason") if results else None,
            }
        elif "mistral" in model_id.lower() or "mixtral" in model_id.lower():
            # Mistral models
            outputs = response_body.get("outputs", [])
            text = outputs[0].get("text", "") if outputs else ""

            return {
                "text": text,
                "input_tokens": None,
                "output_tokens": None,
                "finish_reason": outputs[0].get("stop_reason") if outputs else None,
            }
        else:
            # Try Claude format as default
            content = response_body.get("content", [])
            text = content[0].get("text", "") if content else ""
            usage = response_body.get("usage", {})

            return {
                "text": text,
                "input_tokens": usage.get("input_tokens"),
                "output_tokens": usage.get("output_tokens"),
                "finish_reason": response_body.get("stop_reason"),
            }

    async def validate_credentials(self) -> bool:
        """Validate AWS credentials for Bedrock."""
        try:
            # Try to list foundation models
            self.client.list_foundation_models(maxResults=1)
            return True
        except Exception:
            return False

    def get_available_models(self) -> list[str]:
        """Get available Bedrock models."""
        return [
            "anthropic.claude-3-opus-20240229-v1:0",
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "anthropic.claude-3-haiku-20240307-v1:0",
            "amazon.titan-text-express-v1",
            "mistral.mistral-7b-instruct-v0:2",
            "mistral.mixtral-8x7b-instruct-v0:1",
        ]
