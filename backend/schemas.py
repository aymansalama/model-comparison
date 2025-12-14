"""Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from models import TaskType, RunStatus


# Task schemas
class TaskCreate(BaseModel):
    """Schema for creating a task."""

    task_id: str
    name: str
    description: Optional[str] = None
    task_type: TaskType
    input_fields: List[str]
    label_field: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None
    metrics: List[str]
    prompt_template: str
    splits: Dict[str, str]
    golden_format: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: int
    task_id: str
    name: str
    description: Optional[str]
    task_type: TaskType
    is_builtin: bool
    is_active: bool
    input_fields: List[str]
    label_field: Optional[str]
    metrics: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Model schemas
class ModelResponse(BaseModel):
    """Schema for model response."""

    id: int
    model_id: str
    provider: str
    name: str
    description: Optional[str]
    is_active: bool
    max_tokens: Optional[int]
    supports_json_mode: bool

    class Config:
        from_attributes = True


# Run schemas
class RunConfig(BaseModel):
    """Run configuration."""

    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=512, ge=1, le=4096)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    timeout: int = Field(default=60, ge=1)
    max_retries: int = Field(default=3, ge=0)
    sample_cap: Optional[int] = Field(default=None, ge=1)
    trials: int = Field(default=1, ge=1, le=10)
    split: str = Field(default="test")


class RunCreate(BaseModel):
    """Schema for creating a run."""

    name: Optional[str] = None
    description: Optional[str] = None
    model_ids: List[str] = Field(min_length=1)
    task_ids: List[str] = Field(min_length=1)
    config: RunConfig = Field(default_factory=RunConfig)

    @validator("model_ids")
    def validate_model_ids(cls, v):
        if not v:
            raise ValueError("At least one model must be selected")
        return v

    @validator("task_ids")
    def validate_task_ids(cls, v):
        if not v:
            raise ValueError("At least one task must be selected")
        return v


class RunProgress(BaseModel):
    """Run progress information."""

    total_evaluations: int
    completed_evaluations: int
    failed_evaluations: int
    progress_percent: float
    current_status: str


class RunResponse(BaseModel):
    """Schema for run response."""

    id: int
    run_id: str
    name: Optional[str]
    description: Optional[str]
    status: RunStatus
    config: Dict[str, Any]
    selected_models: List[str]
    selected_tasks: List[str]
    progress_percent: float
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class RunDetailResponse(RunResponse):
    """Detailed run response with progress."""

    total_evaluations: int
    completed_evaluations: int
    failed_evaluations: int
    results_path: Optional[str]


# Result schemas
class MetricResult(BaseModel):
    """Individual metric result."""

    name: str
    value: float
    std: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None


class ResultResponse(BaseModel):
    """Schema for result response."""

    id: int
    task_id: str
    model_id: str
    metrics: Dict[str, Any]
    avg_latency_ms: Optional[float]
    p50_latency_ms: Optional[float]
    p95_latency_ms: Optional[float]
    p99_latency_ms: Optional[float]
    total_input_tokens: Optional[int]
    total_output_tokens: Optional[int]
    estimated_cost_usd: Optional[float]
    num_samples: Optional[int]
    num_errors: int

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    """Leaderboard entry."""

    model_id: str
    task_id: str
    metrics: Dict[str, float]
    avg_latency_ms: Optional[float]
    estimated_cost_usd: Optional[float]


class CredentialStatus(BaseModel):
    """Credential status response."""

    openai_configured: bool
    aws_configured: bool
    openai_valid: Optional[bool] = None
    aws_valid: Optional[bool] = None


# Upload schemas
class UploadResponse(BaseModel):
    """Upload response."""

    task_id: str
    message: str
    validation_warnings: Optional[List[str]] = None


# Export schemas
class ExportFormat(str):
    """Export format enumeration."""

    CSV = "csv"
    JSON = "json"
