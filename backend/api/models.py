"""Models API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Model as DBModel
from schemas import ModelResponse, CredentialStatus
from config import settings

router = APIRouter()


def register_builtin_models():
    """Register built-in models in the database."""
    from database import SessionLocal

    db = SessionLocal()
    try:
        # OpenAI models
        openai_models = [
            # GPT-5 Series
            {"model_id": "gpt-5.2", "provider": "openai", "name": "GPT-5.2", "description": "Latest GPT-5.2 model", "max_tokens": 8192, "supports_json_mode": True},
            {"model_id": "gpt-5.2-pro", "provider": "openai", "name": "GPT-5.2 Pro", "description": "Pro version of GPT-5.2", "max_tokens": 16384, "supports_json_mode": True},
            {"model_id": "gpt-5.2-instant", "provider": "openai", "name": "GPT-5.2 Instant", "description": "Fast GPT-5.2 variant", "max_tokens": 4096, "supports_json_mode": True},
            {"model_id": "gpt-5.1", "provider": "openai", "name": "GPT-5.1", "description": "GPT-5.1 model", "max_tokens": 8192, "supports_json_mode": True},
            {"model_id": "gpt-5-mini", "provider": "openai", "name": "GPT-5 Mini", "description": "Compact GPT-5 model", "max_tokens": 4096, "supports_json_mode": True},
            {"model_id": "gpt-5-nano", "provider": "openai", "name": "GPT-5 Nano", "description": "Ultra-compact GPT-5 model", "max_tokens": 2048, "supports_json_mode": True},

            # GPT-4.1 Series
            {"model_id": "gpt-4.1", "provider": "openai", "name": "GPT-4.1", "description": "Updated GPT-4.1 model", "max_tokens": 8192, "supports_json_mode": True},
            {"model_id": "gpt-4.1-mini", "provider": "openai", "name": "GPT-4.1 Mini", "description": "Compact GPT-4.1 model", "max_tokens": 4096, "supports_json_mode": True},
            {"model_id": "gpt-4.1-nano", "provider": "openai", "name": "GPT-4.1 Nano", "description": "Ultra-compact GPT-4.1 model", "max_tokens": 2048, "supports_json_mode": True},

            # GPT-4o Series
            {"model_id": "gpt-4o", "provider": "openai", "name": "GPT-4o", "description": "Optimized GPT-4 model", "max_tokens": 8192, "supports_json_mode": True},
            {"model_id": "gpt-4o-mini", "provider": "openai", "name": "GPT-4o Mini", "description": "Compact GPT-4o model", "max_tokens": 4096, "supports_json_mode": True},

            # GPT-OSS Series
            {"model_id": "gpt-oss-120b", "provider": "openai", "name": "GPT-OSS 120B", "description": "120B parameter open-source GPT", "max_tokens": 4096, "supports_json_mode": True},
            {"model_id": "gpt-oss-20b", "provider": "openai", "name": "GPT-OSS 20B", "description": "20B parameter open-source GPT", "max_tokens": 4096, "supports_json_mode": True},

            # O-Series (Reasoning Models)
            {"model_id": "o3", "provider": "openai", "name": "O3", "description": "Advanced reasoning model O3", "max_tokens": 8192, "supports_json_mode": True},
            {"model_id": "o3-mini", "provider": "openai", "name": "O3 Mini", "description": "Compact O3 reasoning model", "max_tokens": 4096, "supports_json_mode": True},
            {"model_id": "o4-mini", "provider": "openai", "name": "O4 Mini", "description": "Next-gen compact reasoning model", "max_tokens": 4096, "supports_json_mode": True},

            # Legacy models (keeping for backward compatibility)
            {"model_id": "gpt-4-turbo-preview", "provider": "openai", "name": "GPT-4 Turbo", "description": "Most capable GPT-4 model with 128K context", "max_tokens": 4096, "supports_json_mode": True},
            {"model_id": "gpt-4", "provider": "openai", "name": "GPT-4", "description": "Standard GPT-4 model", "max_tokens": 8192, "supports_json_mode": False},
            {"model_id": "gpt-3.5-turbo", "provider": "openai", "name": "GPT-3.5 Turbo", "description": "Fast and efficient model", "max_tokens": 4096, "supports_json_mode": True},
        ]

        # Bedrock models - OpenAI via Bedrock
        bedrock_openai = [
            {"model_id": "openai.gpt-oss-20b-1:0", "provider": "bedrock", "name": "GPT-OSS 20B (Bedrock)", "description": "20B parameter GPT via Bedrock", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "openai.gpt-oss-120b-1:0", "provider": "bedrock", "name": "GPT-OSS 120B (Bedrock)", "description": "120B parameter GPT via Bedrock", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "openai.gpt-oss-safeguard-20b", "provider": "bedrock", "name": "GPT-OSS Safeguard 20B", "description": "Safety-enhanced 20B GPT", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "openai.gpt-oss-safeguard-120b", "provider": "bedrock", "name": "GPT-OSS Safeguard 120B", "description": "Safety-enhanced 120B GPT", "max_tokens": 4096, "supports_json_mode": False},
        ]

        # Bedrock models - Anthropic Claude
        bedrock_anthropic = [
            {"model_id": "anthropic.claude-4-opus", "provider": "bedrock", "name": "Claude 4 Opus", "description": "Most capable Claude 4 model", "max_tokens": 8192, "supports_json_mode": False},
            {"model_id": "anthropic.claude-4-sonnet", "provider": "bedrock", "name": "Claude 4 Sonnet", "description": "Balanced Claude 4 model", "max_tokens": 8192, "supports_json_mode": False},
            {"model_id": "anthropic.claude-4-haiku", "provider": "bedrock", "name": "Claude 4 Haiku", "description": "Fast Claude 4 model", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "anthropic.claude-4.5-opus", "provider": "bedrock", "name": "Claude 4.5 Opus", "description": "Enhanced Claude 4.5 Opus", "max_tokens": 8192, "supports_json_mode": False},
            {"model_id": "anthropic.claude-4.5-sonnet", "provider": "bedrock", "name": "Claude 4.5 Sonnet", "description": "Enhanced Claude 4.5 Sonnet", "max_tokens": 8192, "supports_json_mode": False},
            {"model_id": "anthropic.claude-3.5-sonnet", "provider": "bedrock", "name": "Claude 3.5 Sonnet", "description": "Enhanced Claude 3.5 Sonnet", "max_tokens": 8192, "supports_json_mode": False},
            {"model_id": "anthropic.claude-3-opus", "provider": "bedrock", "name": "Claude 3 Opus", "description": "Most capable Claude 3 model", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "anthropic.claude-3-sonnet", "provider": "bedrock", "name": "Claude 3 Sonnet", "description": "Balanced Claude 3 model", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "anthropic.claude-3-haiku", "provider": "bedrock", "name": "Claude 3 Haiku", "description": "Fast Claude 3 model", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "anthropic.claude-instant", "provider": "bedrock", "name": "Claude Instant", "description": "Ultra-fast Claude model", "max_tokens": 2048, "supports_json_mode": False},
            # Legacy with version tags
            {"model_id": "anthropic.claude-3-opus-20240229-v1:0", "provider": "bedrock", "name": "Claude 3 Opus (v1)", "description": "Claude 3 Opus with version tag", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "anthropic.claude-3-sonnet-20240229-v1:0", "provider": "bedrock", "name": "Claude 3 Sonnet (v1)", "description": "Claude 3 Sonnet with version tag", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "anthropic.claude-3-haiku-20240307-v1:0", "provider": "bedrock", "name": "Claude 3 Haiku (v1)", "description": "Claude 3 Haiku with version tag", "max_tokens": 4096, "supports_json_mode": False},
        ]

        # Bedrock models - AI21
        bedrock_ai21 = [
            {"model_id": "ai21.jamba-instruct", "provider": "bedrock", "name": "Jamba Instruct", "description": "AI21 Jamba instruction-tuned model", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "ai21.jamba-1.5-large", "provider": "bedrock", "name": "Jamba 1.5 Large", "description": "AI21 Jamba 1.5 large model", "max_tokens": 8192, "supports_json_mode": False},
            {"model_id": "ai21.jurassic-2-ultra", "provider": "bedrock", "name": "Jurassic-2 Ultra", "description": "AI21 Jurassic-2 ultra model", "max_tokens": 8192, "supports_json_mode": False},
            {"model_id": "ai21.jurassic-2-mid", "provider": "bedrock", "name": "Jurassic-2 Mid", "description": "AI21 Jurassic-2 mid model", "max_tokens": 4096, "supports_json_mode": False},
        ]

        # Bedrock models - Cohere
        bedrock_cohere = [
            {"model_id": "cohere.command", "provider": "bedrock", "name": "Cohere Command", "description": "Cohere Command model", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "cohere.command-light", "provider": "bedrock", "name": "Cohere Command Light", "description": "Lightweight Cohere Command model", "max_tokens": 4096, "supports_json_mode": False},
        ]

        # Bedrock models - Mistral
        bedrock_mistral = [
            {"model_id": "mistral.large", "provider": "bedrock", "name": "Mistral Large", "description": "Mistral's largest model", "max_tokens": 8192, "supports_json_mode": False},
            {"model_id": "mistral.large-3", "provider": "bedrock", "name": "Mistral Large 3", "description": "Mistral Large version 3", "max_tokens": 8192, "supports_json_mode": False},
            {"model_id": "mistral.medium", "provider": "bedrock", "name": "Mistral Medium", "description": "Mistral medium-sized model", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "mistral.small", "provider": "bedrock", "name": "Mistral Small", "description": "Mistral small model", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "ministral-3b", "provider": "bedrock", "name": "Ministral 3B", "description": "Compact 3B parameter Mistral", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "ministral-8b", "provider": "bedrock", "name": "Ministral 8B", "description": "8B parameter Mistral", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "ministral-14b", "provider": "bedrock", "name": "Ministral 14B", "description": "14B parameter Mistral", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "magistral-small-1.2", "provider": "bedrock", "name": "Magistral Small 1.2", "description": "Magistral small model v1.2", "max_tokens": 4096, "supports_json_mode": False},
        ]

        # Bedrock models - Meta Llama
        bedrock_meta = [
            {"model_id": "meta.llama2-13b-chat", "provider": "bedrock", "name": "Llama 2 13B Chat", "description": "Meta Llama 2 13B chat model", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "meta.llama2-70b-chat", "provider": "bedrock", "name": "Llama 2 70B Chat", "description": "Meta Llama 2 70B chat model", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "meta.llama3-8b-instruct", "provider": "bedrock", "name": "Llama 3 8B Instruct", "description": "Meta Llama 3 8B instruction model", "max_tokens": 4096, "supports_json_mode": False},
            {"model_id": "meta.llama3-70b-instruct", "provider": "bedrock", "name": "Llama 3 70B Instruct", "description": "Meta Llama 3 70B instruction model", "max_tokens": 4096, "supports_json_mode": False},
        ]

        # Bedrock models - NVIDIA
        bedrock_nvidia = [
            {"model_id": "nvidia.nemotron-nano-2-9b", "provider": "bedrock", "name": "Nemotron Nano 2 9B", "description": "NVIDIA Nemotron nano 9B model", "max_tokens": 4096, "supports_json_mode": False},
        ]

        # Bedrock models - Qwen
        bedrock_qwen = [
            {"model_id": "qwen.qwen3-next-80b-a3b", "provider": "bedrock", "name": "Qwen3 Next 80B", "description": "Qwen 3 Next 80B model", "max_tokens": 8192, "supports_json_mode": False},
        ]

        # Bedrock models - Moonshot
        bedrock_moonshot = [
            {"model_id": "moonshot.kimi-k2-thinking", "provider": "bedrock", "name": "Kimi K2 Thinking", "description": "Moonshot Kimi K2 reasoning model", "max_tokens": 8192, "supports_json_mode": False},
        ]

        # Combine all models
        all_models = (
            openai_models +
            bedrock_openai +
            bedrock_anthropic +
            bedrock_ai21 +
            bedrock_cohere +
            bedrock_mistral +
            bedrock_meta +
            bedrock_nvidia +
            bedrock_qwen +
            bedrock_moonshot
        )

        for model_data in all_models:
            # Check if model already exists
            existing = (
                db.query(DBModel)
                .filter(DBModel.model_id == model_data["model_id"])
                .first()
            )
            if existing:
                continue

            # Create new model
            model = DBModel(**model_data)
            db.add(model)

        db.commit()
    finally:
        db.close()


@router.get("/models", response_model=List[ModelResponse])
async def list_models(db: Session = Depends(get_db)):
    """
    List all available models.

    Returns list of models grouped by provider.
    """
    models = db.query(DBModel).filter(DBModel.is_active == True).all()
    return models


@router.get("/models/credentials", response_model=CredentialStatus)
async def check_credentials():
    """
    Check provider credential status.

    Returns whether credentials are configured and valid.
    """
    status = CredentialStatus(
        openai_configured=bool(settings.OPENAI_API_KEY),
        aws_configured=True,  # AWS credentials checked via boto3 default chain
    )

    # Optionally validate credentials
    try:
        if settings.OPENAI_API_KEY:
            from providers import OpenAIClient

            client = OpenAIClient()
            status.openai_valid = await client.validate_credentials()
    except Exception:
        status.openai_valid = False

    try:
        from providers import BedrockClient

        client = BedrockClient()
        status.aws_valid = await client.validate_credentials()
    except Exception:
        status.aws_valid = False

    return status
