"""Task and dataset loader."""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datasets import load_dataset
from jinja2 import Template
from config import settings
from .builtin_tasks import BUILTIN_TASKS


class TaskLoader:
    """Load and prepare tasks and datasets."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize task loader.

        Args:
            storage_dir: Directory for storing datasets
        """
        self.storage_dir = storage_dir or settings.DATASETS_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def load_builtin_dataset(
        self,
        task_id: str,
        split: str = "test",
        sample_cap: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Load a built-in dataset from HuggingFace.

        Args:
            task_id: Built-in task ID
            split: Dataset split (train, validation, test)
            sample_cap: Maximum number of samples to load

        Returns:
            List of dataset samples
        """
        if task_id not in BUILTIN_TASKS:
            raise ValueError(f"Unknown built-in task: {task_id}")

        task_def = BUILTIN_TASKS[task_id]
        dataset_name = task_def["dataset_name"]
        dataset_config = task_def.get("dataset_config")

        try:
            # Load from HuggingFace
            if dataset_config:
                dataset = load_dataset(dataset_name, dataset_config, split=split)
            else:
                dataset = load_dataset(dataset_name, split=split)

            # Convert to list of dicts
            samples = []
            for i, item in enumerate(dataset):
                if sample_cap and i >= sample_cap:
                    break
                samples.append(dict(item))

            return samples

        except Exception as e:
            raise RuntimeError(f"Failed to load dataset {dataset_name}: {e}")

    def load_custom_dataset(
        self,
        task_id: str,
        file_path: Path,
        split: str = "test",
        sample_cap: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Load a custom dataset from file.

        Args:
            task_id: Custom task ID
            file_path: Path to dataset file (JSONL or CSV)
            split: Dataset split name
            sample_cap: Maximum number of samples to load

        Returns:
            List of dataset samples
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")

        samples = []

        if file_path.suffix == ".jsonl":
            with open(file_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if sample_cap and i >= sample_cap:
                        break
                    samples.append(json.loads(line))

        elif file_path.suffix == ".csv":
            import pandas as pd

            df = pd.read_csv(file_path)
            if sample_cap:
                df = df.head(sample_cap)
            samples = df.to_dict("records")

        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        # Filter by split if split column exists
        if samples and "split" in samples[0]:
            samples = [s for s in samples if s.get("split") == split]

        return samples

    def prepare_prompt(
        self,
        template: str,
        sample: Dict[str, Any],
    ) -> str:
        """
        Prepare a prompt from a template and sample data.

        Args:
            template: Jinja2 prompt template
            sample: Sample data dictionary

        Returns:
            Rendered prompt string
        """
        jinja_template = Template(template)
        return jinja_template.render(**sample)

    def extract_label(
        self,
        sample: Dict[str, Any],
        label_field: str,
        task_type: str,
        label_mapping: Optional[Dict[int, str]] = None,
    ) -> Any:
        """
        Extract and format the ground truth label from a sample.

        Args:
            sample: Sample data dictionary
            label_field: Name of the label field
            task_type: Type of task
            label_mapping: Optional mapping from numeric labels to strings

        Returns:
            Formatted label
        """
        if label_field not in sample:
            return None

        label = sample[label_field]

        # Apply label mapping if provided
        if label_mapping and isinstance(label, int):
            label = label_mapping.get(label, label)

        # Handle different task types
        if task_type == "qa":
            # SQuAD format: answers is a dict with 'text' list
            if isinstance(label, dict) and "text" in label:
                texts = label["text"]
                return texts[0] if texts else ""
            return label

        elif task_type == "ner":
            # NER tags are typically lists of integers
            return label

        elif task_type == "similarity":
            # Ensure float for similarity tasks
            return float(label)

        else:
            # Default: return as-is (for classification, etc.)
            return label

    def parse_model_output(
        self,
        output: str,
        task_type: str,
    ) -> Any:
        """
        Parse model output based on task type.

        Args:
            output: Raw model output string
            task_type: Type of task

        Returns:
            Parsed output in appropriate format
        """
        output = output.strip()

        if task_type == "classification" or task_type == "nli":
            # Extract first word/phrase as class label
            output = output.lower()
            # Try to extract the class from common formats
            if ":" in output:
                output = output.split(":", 1)[1].strip()
            return output.split()[0] if output else ""

        elif task_type == "similarity":
            # Extract numeric score
            import re

            match = re.search(r"[-+]?\d*\.?\d+", output)
            if match:
                try:
                    score = float(match.group())
                    # Clamp to 0-5 range for STS-B
                    return max(0.0, min(5.0, score))
                except ValueError:
                    return 2.5  # Default middle value
            return 2.5

        elif task_type == "ner":
            # Try to parse JSON output
            try:
                entities = json.loads(output)
                # Convert to IOB tags (simplified)
                return entities
            except json.JSONDecodeError:
                return []

        elif task_type == "qa":
            # Return the answer text
            return output

        elif task_type in ["summarization", "translation", "freeform"]:
            # Return as-is
            return output

        else:
            return output
