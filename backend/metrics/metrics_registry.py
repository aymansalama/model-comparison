"""Registry of supported metrics by task type."""

METRICS_REGISTRY = {
    "classification": {
        "supported_metrics": ["accuracy", "f1_macro", "f1_micro", "f1_weighted", "precision", "recall"],
        "default_metrics": ["accuracy", "f1_macro"],
        "primary_metric": "accuracy",
    },
    "multilabel": {
        "supported_metrics": ["f1_micro", "f1_macro", "f1_weighted", "precision", "recall"],
        "default_metrics": ["f1_micro", "f1_macro"],
        "primary_metric": "f1_micro",
    },
    "ner": {
        "supported_metrics": ["ner_f1", "ner_precision", "ner_recall"],
        "default_metrics": ["ner_f1", "ner_precision", "ner_recall"],
        "primary_metric": "ner_f1",
    },
    "summarization": {
        "supported_metrics": ["rouge1", "rouge2", "rougeL"],
        "default_metrics": ["rouge1", "rouge2", "rougeL"],
        "primary_metric": "rougeL",
    },
    "qa": {
        "supported_metrics": ["exact_match", "f1_qa"],
        "default_metrics": ["exact_match", "f1_qa"],
        "primary_metric": "f1_qa",
    },
    "similarity": {
        "supported_metrics": ["pearson", "spearman"],
        "default_metrics": ["pearson", "spearman"],
        "primary_metric": "pearson",
    },
    "nli": {
        "supported_metrics": ["accuracy", "f1_macro"],
        "default_metrics": ["accuracy", "f1_macro"],
        "primary_metric": "accuracy",
    },
    "translation": {
        "supported_metrics": ["bleu", "chrf"],
        "default_metrics": ["bleu", "chrf"],
        "primary_metric": "bleu",
    },
    "freeform": {
        "supported_metrics": ["rouge1", "rouge2", "rougeL"],
        "default_metrics": ["rougeL"],
        "primary_metric": "rougeL",
    },
}


def get_supported_metrics(task_type: str) -> list[str]:
    """Get supported metrics for a task type."""
    return METRICS_REGISTRY.get(task_type, {}).get("supported_metrics", [])


def get_default_metrics(task_type: str) -> list[str]:
    """Get default metrics for a task type."""
    return METRICS_REGISTRY.get(task_type, {}).get("default_metrics", [])


def get_primary_metric(task_type: str) -> str:
    """Get primary metric for a task type."""
    return METRICS_REGISTRY.get(task_type, {}).get("primary_metric", "accuracy")


def validate_metrics(task_type: str, metrics: list[str]) -> bool:
    """Validate that metrics are supported for task type."""
    supported = get_supported_metrics(task_type)
    return all(metric in supported for metric in metrics)
