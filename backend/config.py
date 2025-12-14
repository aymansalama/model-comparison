"""Application configuration."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    API_TITLE: str = "NLP Benchmark Platform"
    API_VERSION: str = "1.0.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./storage/benchmark.db"

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Storage
    STORAGE_ROOT: Path = Path("./storage")
    UPLOAD_DIR: Path = Path("./storage/uploads")
    CUSTOM_TASKS_DIR: Path = Path("./storage/custom_tasks")
    RESULTS_DIR: Path = Path("./storage/results")
    DATASETS_DIR: Path = Path("./storage/datasets")

    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: set = {".zip", ".jsonl", ".csv"}

    # Provider credentials
    OPENAI_API_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # Model pricing (USD per 1K tokens)
    MODEL_PRICING: dict = {
        # OpenAI GPT-5 Series (estimated pricing)
        "gpt-5.2": {"input": 0.02, "output": 0.06},
        "gpt-5.2-pro": {"input": 0.03, "output": 0.09},
        "gpt-5.2-instant": {"input": 0.01, "output": 0.03},
        "gpt-5.1": {"input": 0.015, "output": 0.045},
        "gpt-5-mini": {"input": 0.005, "output": 0.015},
        "gpt-5-nano": {"input": 0.001, "output": 0.003},

        # OpenAI GPT-4.1 Series (estimated pricing)
        "gpt-4.1": {"input": 0.012, "output": 0.036},
        "gpt-4.1-mini": {"input": 0.006, "output": 0.018},
        "gpt-4.1-nano": {"input": 0.002, "output": 0.006},

        # OpenAI GPT-4o Series
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.0015, "output": 0.006},

        # OpenAI GPT-OSS Series
        "gpt-oss-120b": {"input": 0.003, "output": 0.009},
        "gpt-oss-20b": {"input": 0.001, "output": 0.003},

        # OpenAI O-Series (Reasoning models - estimated pricing)
        "o3": {"input": 0.025, "output": 0.075},
        "o3-mini": {"input": 0.01, "output": 0.03},
        "o4-mini": {"input": 0.012, "output": 0.036},

        # Legacy OpenAI models
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},

        # Claude 4 Series (estimated pricing)
        "anthropic.claude-4-opus": {"input": 0.025, "output": 0.125},
        "anthropic.claude-4-sonnet": {"input": 0.005, "output": 0.025},
        "anthropic.claude-4-haiku": {"input": 0.0005, "output": 0.0025},
        "anthropic.claude-4.5-opus": {"input": 0.03, "output": 0.15},
        "anthropic.claude-4.5-sonnet": {"input": 0.006, "output": 0.03},

        # Claude 3.5 Series
        "anthropic.claude-3.5-sonnet": {"input": 0.003, "output": 0.015},

        # Claude 3 Series
        "anthropic.claude-3-opus": {"input": 0.015, "output": 0.075},
        "anthropic.claude-3-opus-20240229-v1:0": {"input": 0.015, "output": 0.075},
        "anthropic.claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "anthropic.claude-3-sonnet-20240229-v1:0": {"input": 0.003, "output": 0.015},
        "anthropic.claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "anthropic.claude-3-haiku-20240307-v1:0": {"input": 0.00025, "output": 0.00125},
        "anthropic.claude-instant": {"input": 0.0001, "output": 0.0003},

        # Meta Llama (estimated pricing)
        "meta.llama2-13b-chat": {"input": 0.0002, "output": 0.0004},
        "meta.llama2-70b-chat": {"input": 0.0005, "output": 0.001},
        "meta.llama3-8b-instruct": {"input": 0.0002, "output": 0.0004},
        "meta.llama3-70b-instruct": {"input": 0.0005, "output": 0.001},

        # Mistral Series (estimated pricing)
        "mistral.large": {"input": 0.002, "output": 0.006},
        "mistral.large-3": {"input": 0.003, "output": 0.009},
        "mistral.medium": {"input": 0.001, "output": 0.003},
        "mistral.small": {"input": 0.0005, "output": 0.0015},
    }

    # Benchmark defaults
    DEFAULT_TEMPERATURE: float = 0.0
    DEFAULT_MAX_TOKENS: int = 512
    DEFAULT_TOP_P: float = 1.0
    DEFAULT_TIMEOUT: int = 60
    DEFAULT_MAX_RETRIES: int = 3
    DEFAULT_SAMPLE_CAP: Optional[int] = None
    DEFAULT_TRIALS: int = 1

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create storage directories
        for directory in [
            self.STORAGE_ROOT,
            self.UPLOAD_DIR,
            self.CUSTOM_TASKS_DIR,
            self.RESULTS_DIR,
            self.DATASETS_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
