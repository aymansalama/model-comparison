"""Database models."""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class TaskType(str, enum.Enum):
    """Task type enumeration."""

    CLASSIFICATION = "classification"
    MULTILABEL = "multilabel"
    NER = "ner"
    SUMMARIZATION = "summarization"
    QA = "qa"
    SIMILARITY = "similarity"
    NLI = "nli"
    TRANSLATION = "translation"
    FREEFORM = "freeform"


class RunStatus(str, enum.Enum):
    """Run status enumeration."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(Base):
    """Task model."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    task_type = Column(SQLEnum(TaskType), nullable=False)
    is_builtin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Task configuration
    input_fields = Column(JSON)  # List of field names
    label_field = Column(String)
    schema = Column(JSON)  # Expected output schema
    metrics = Column(JSON)  # List of metric names
    prompt_template = Column(Text)
    splits = Column(JSON)  # Dict mapping split names to file paths
    golden_format = Column(JSON)  # Rules for interpreting labels

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    storage_path = Column(String)  # Path to task files

    # Relationships
    datasets = relationship("Dataset", back_populates="task", cascade="all, delete-orphan")
    run_tasks = relationship("RunTask", back_populates="task")


class Dataset(Base):
    """Dataset model."""

    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    name = Column(String, nullable=False)
    split = Column(String, nullable=False)  # train, validation, test
    file_path = Column(String, nullable=False)
    num_samples = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    task = relationship("Task", back_populates="datasets")


class Model(Base):
    """Model registry."""

    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String, unique=True, nullable=False, index=True)
    provider = Column(String, nullable=False)  # openai, bedrock
    name = Column(String, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    max_tokens = Column(Integer)
    supports_json_mode = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    run_models = relationship("RunModel", back_populates="model")


class Run(Base):
    """Benchmark run."""

    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    description = Column(Text)
    status = Column(SQLEnum(RunStatus), default=RunStatus.QUEUED)

    # Configuration
    config = Column(JSON)  # Run configuration (temperature, max_tokens, etc.)
    selected_models = Column(JSON)  # List of model IDs
    selected_tasks = Column(JSON)  # List of task IDs

    # Progress tracking
    total_evaluations = Column(Integer, default=0)
    completed_evaluations = Column(Integer, default=0)
    failed_evaluations = Column(Integer, default=0)
    progress_percent = Column(Float, default=0.0)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Results
    results_path = Column(String)  # Path to results directory
    error_message = Column(Text)

    # Celery task ID
    celery_task_id = Column(String)

    # Relationships
    run_tasks = relationship("RunTask", back_populates="run", cascade="all, delete-orphan")
    run_models = relationship("RunModel", back_populates="run", cascade="all, delete-orphan")
    results = relationship("Result", back_populates="run", cascade="all, delete-orphan")


class RunTask(Base):
    """Many-to-many relationship between runs and tasks."""

    __tablename__ = "run_tasks"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    # Relationships
    run = relationship("Run", back_populates="run_tasks")
    task = relationship("Task", back_populates="run_tasks")


class RunModel(Base):
    """Many-to-many relationship between runs and models."""

    __tablename__ = "run_models"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)

    # Relationships
    run = relationship("Run", back_populates="run_models")
    model = relationship("Model", back_populates="run_models")


class Result(Base):
    """Evaluation results."""

    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False)
    task_id = Column(String, nullable=False)
    model_id = Column(String, nullable=False)

    # Metrics (stored as JSON for flexibility)
    metrics = Column(JSON)

    # Performance stats
    avg_latency_ms = Column(Float)
    p50_latency_ms = Column(Float)
    p95_latency_ms = Column(Float)
    p99_latency_ms = Column(Float)

    # Token usage
    total_input_tokens = Column(Integer)
    total_output_tokens = Column(Integer)
    estimated_cost_usd = Column(Float)

    # Artifacts
    raw_outputs_path = Column(String)
    metrics_path = Column(String)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    num_samples = Column(Integer)
    num_errors = Column(Integer, default=0)

    # Relationships
    run = relationship("Run", back_populates="results")
