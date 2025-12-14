"""Custom task upload validation."""
import zipfile
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import yaml
from pydantic import BaseModel, Field, validator
from models import TaskType
from config import settings


class TaskDefinition(BaseModel):
    """Task definition schema for validation."""

    task_id: str = Field(..., pattern=r"^[a-z0-9_]+$")
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

    @validator("task_id")
    def validate_task_id(cls, v):
        if len(v) < 2 or len(v) > 50:
            raise ValueError("task_id must be between 2 and 50 characters")
        return v

    @validator("splits")
    def validate_splits(cls, v):
        if not v:
            raise ValueError("At least one split must be defined")
        for split_name, file_path in v.items():
            if not file_path:
                raise ValueError(f"File path for split '{split_name}' cannot be empty")
        return v

    @validator("metrics")
    def validate_metrics(cls, v):
        if not v:
            raise ValueError("At least one metric must be specified")
        return v


class UploadValidator:
    """Validator for custom task uploads."""

    def __init__(self):
        """Initialize upload validator."""
        self.max_file_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS

    def validate_upload(
        self,
        file_path: Path,
        file_size: int,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file.

        Args:
            file_path: Path to uploaded file
            file_size: Size of uploaded file in bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if file_size > self.max_file_size:
            return False, f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"

        # Check file extension
        if file_path.suffix not in self.allowed_extensions:
            return False, f"File extension '{file_path.suffix}' not allowed. Allowed extensions: {self.allowed_extensions}"

        # Check if it's a valid zip file
        if file_path.suffix == ".zip":
            if not zipfile.is_zipfile(file_path):
                return False, "Invalid ZIP file"

            # Check for zip slip vulnerability
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                for member in zip_ref.namelist():
                    # Normalize path and check for directory traversal
                    member_path = Path(member)
                    if member_path.is_absolute() or ".." in member_path.parts:
                        return False, "ZIP file contains unsafe paths (directory traversal attempt)"

        return True, None

    def extract_and_validate_task(
        self,
        zip_path: Path,
        extract_dir: Path,
    ) -> Tuple[Optional[TaskDefinition], List[str], Optional[str]]:
        """
        Extract and validate task from ZIP file.

        Args:
            zip_path: Path to ZIP file
            extract_dir: Directory to extract to

        Returns:
            Tuple of (task_definition, warnings, error_message)
        """
        warnings = []

        try:
            # Extract ZIP file
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            # Look for task.yaml or task.yml
            task_yaml_path = extract_dir / "task.yaml"
            task_yml_path = extract_dir / "task.yml"

            if task_yaml_path.exists():
                config_path = task_yaml_path
            elif task_yml_path.exists():
                config_path = task_yml_path
            else:
                return None, warnings, "task.yaml not found in ZIP file"

            # Load and parse task.yaml
            with open(config_path, "r", encoding="utf-8") as f:
                task_config = yaml.safe_load(f)

            # Validate task definition
            try:
                task_def = TaskDefinition(**task_config)
            except Exception as e:
                return None, warnings, f"Invalid task definition: {str(e)}"

            # Validate dataset files exist
            for split_name, file_name in task_def.splits.items():
                file_path = extract_dir / file_name
                if not file_path.exists():
                    return None, warnings, f"Dataset file '{file_name}' for split '{split_name}' not found"

                # Validate dataset format and sample
                valid, error = self._validate_dataset_file(file_path, task_def)
                if not valid:
                    return None, warnings, error

            # Check for README
            if not (extract_dir / "README.md").exists():
                warnings.append("No README.md found in upload")

            return task_def, warnings, None

        except Exception as e:
            return None, warnings, f"Error extracting task: {str(e)}"

    def _validate_dataset_file(
        self,
        file_path: Path,
        task_def: TaskDefinition,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate dataset file format and contents.

        Args:
            file_path: Path to dataset file
            task_def: Task definition

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Read first few samples
            samples = []
            max_samples = 10

            if file_path.suffix == ".jsonl":
                with open(file_path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if i >= max_samples:
                            break
                        try:
                            sample = json.loads(line)
                            samples.append(sample)
                        except json.JSONDecodeError as e:
                            return False, f"Invalid JSON at line {i + 1}: {str(e)}"

            elif file_path.suffix == ".csv":
                import pandas as pd

                try:
                    df = pd.read_csv(file_path, nrows=max_samples)
                    samples = df.to_dict("records")
                except Exception as e:
                    return False, f"Error reading CSV file: {str(e)}"

            else:
                return False, f"Unsupported dataset file format: {file_path.suffix}"

            # Validate samples have required fields
            if not samples:
                return False, "Dataset file is empty"

            for i, sample in enumerate(samples):
                # Check input fields
                for field in task_def.input_fields:
                    if field not in sample:
                        return False, f"Sample {i + 1} missing required input field: {field}"

                # Check label field
                if task_def.label_field and task_def.label_field not in sample:
                    return False, f"Sample {i + 1} missing required label field: {task_def.label_field}"

            return True, None

        except Exception as e:
            return False, f"Error validating dataset file: {str(e)}"

    def check_task_id_unique(self, task_id: str, db) -> bool:
        """
        Check if task_id is unique in database.

        Args:
            task_id: Task ID to check
            db: Database session

        Returns:
            True if unique, False if already exists
        """
        from models import Task

        existing = db.query(Task).filter(Task.task_id == task_id).first()
        return existing is None
