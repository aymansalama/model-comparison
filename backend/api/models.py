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
            {
                "model_id": "gpt-4-turbo-preview",
                "provider": "openai",
                "name": "GPT-4 Turbo",
                "description": "Most capable GPT-4 model with 128K context",
                "max_tokens": 4096,
                "supports_json_mode": True,
            },
            {
                "model_id": "gpt-4",
                "provider": "openai",
                "name": "GPT-4",
                "description": "Standard GPT-4 model",
                "max_tokens": 8192,
                "supports_json_mode": False,
            },
            {
                "model_id": "gpt-3.5-turbo",
                "provider": "openai",
                "name": "GPT-3.5 Turbo",
                "description": "Fast and efficient model",
                "max_tokens": 4096,
                "supports_json_mode": True,
            },
        ]

        # Bedrock models
        bedrock_models = [
            {
                "model_id": "anthropic.claude-3-opus-20240229-v1:0",
                "provider": "bedrock",
                "name": "Claude 3 Opus",
                "description": "Most capable Claude model",
                "max_tokens": 4096,
                "supports_json_mode": False,
            },
            {
                "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
                "provider": "bedrock",
                "name": "Claude 3 Sonnet",
                "description": "Balanced Claude model",
                "max_tokens": 4096,
                "supports_json_mode": False,
            },
            {
                "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
                "provider": "bedrock",
                "name": "Claude 3 Haiku",
                "description": "Fast Claude model",
                "max_tokens": 4096,
                "supports_json_mode": False,
            },
        ]

        all_models = openai_models + bedrock_models

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
