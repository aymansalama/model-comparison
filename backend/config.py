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
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
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
