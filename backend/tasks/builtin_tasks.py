"""Built-in task definitions."""
from typing import Dict, Any

BUILTIN_TASKS = {
    "sst2": {
        "task_id": "sst2",
        "name": "SST-2 Sentiment Analysis",
        "description": "Stanford Sentiment Treebank binary sentiment classification",
        "task_type": "classification",
        "input_fields": ["sentence"],
        "label_field": "label",
        "metrics": ["accuracy", "f1_macro"],
        "prompt_template": "Classify the sentiment of the following sentence as either 'positive' or 'negative'.\n\nSentence: {{ sentence }}\n\nSentiment:",
        "dataset_name": "glue",
        "dataset_config": "sst2",
        "label_mapping": {0: "negative", 1: "positive"},
    },
    "ag_news": {
        "task_id": "ag_news",
        "name": "AG News Topic Classification",
        "description": "News article topic classification into 4 categories",
        "task_type": "classification",
        "input_fields": ["text"],
        "label_field": "label",
        "metrics": ["accuracy", "f1_macro"],
        "prompt_template": "Classify the following news article into one of these categories: World, Sports, Business, or Sci/Tech.\n\nArticle: {{ text }}\n\nCategory:",
        "dataset_name": "ag_news",
        "dataset_config": None,
        "label_mapping": {0: "World", 1: "Sports", 2: "Business", 3: "Sci/Tech"},
    },
    "conll2003": {
        "task_id": "conll2003",
        "name": "CoNLL-2003 Named Entity Recognition",
        "description": "Named entity recognition for Person, Organization, Location, and Miscellaneous",
        "task_type": "ner",
        "input_fields": ["tokens"],
        "label_field": "ner_tags",
        "metrics": ["ner_f1", "ner_precision", "ner_recall"],
        "prompt_template": "Extract named entities from the following text. Return a JSON list of entities with their types (PER, ORG, LOC, MISC).\n\nText: {{ tokens | join(' ') }}\n\nEntities:",
        "dataset_name": "conll2003",
        "dataset_config": None,
        "ner_tags": ["O", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC", "B-MISC", "I-MISC"],
    },
    "xsum": {
        "task_id": "xsum",
        "name": "XSum Summarization",
        "description": "Extreme summarization of BBC articles",
        "task_type": "summarization",
        "input_fields": ["document"],
        "label_field": "summary",
        "metrics": ["rouge1", "rouge2", "rougeL"],
        "prompt_template": "Summarize the following article in one sentence.\n\nArticle: {{ document }}\n\nSummary:",
        "dataset_name": "xsum",
        "dataset_config": None,
    },
    "squad_v2": {
        "task_id": "squad_v2",
        "name": "SQuAD v2 Question Answering",
        "description": "Question answering with unanswerable questions",
        "task_type": "qa",
        "input_fields": ["context", "question"],
        "label_field": "answers",
        "metrics": ["exact_match", "f1_qa"],
        "prompt_template": "Answer the following question based on the context. If the question cannot be answered based on the context, respond with 'unanswerable'.\n\nContext: {{ context }}\n\nQuestion: {{ question }}\n\nAnswer:",
        "dataset_name": "squad_v2",
        "dataset_config": None,
    },
    "stsb": {
        "task_id": "stsb",
        "name": "STS-B Semantic Similarity",
        "description": "Semantic textual similarity on a 0-5 scale",
        "task_type": "similarity",
        "input_fields": ["sentence1", "sentence2"],
        "label_field": "label",
        "metrics": ["pearson", "spearman"],
        "prompt_template": "Rate the semantic similarity between the following two sentences on a scale from 0 (completely dissimilar) to 5 (completely similar). Respond with only a number.\n\nSentence 1: {{ sentence1 }}\nSentence 2: {{ sentence2 }}\n\nSimilarity score:",
        "dataset_name": "glue",
        "dataset_config": "stsb",
    },
    "mnli": {
        "task_id": "mnli",
        "name": "MNLI Natural Language Inference",
        "description": "Multi-Genre Natural Language Inference",
        "task_type": "nli",
        "input_fields": ["premise", "hypothesis"],
        "label_field": "label",
        "metrics": ["accuracy", "f1_macro"],
        "prompt_template": "Determine the relationship between the premise and hypothesis. Choose one: entailment, neutral, or contradiction.\n\nPremise: {{ premise }}\nHypothesis: {{ hypothesis }}\n\nRelationship:",
        "dataset_name": "glue",
        "dataset_config": "mnli",
        "label_mapping": {0: "entailment", 1: "neutral", 2: "contradiction"},
    },
    "opus_books": {
        "task_id": "opus_books",
        "name": "OPUS Books Translation (en-fr)",
        "description": "English to French translation from books",
        "task_type": "translation",
        "input_fields": ["en"],
        "label_field": "fr",
        "metrics": ["bleu", "chrf"],
        "prompt_template": "Translate the following English text to French.\n\nEnglish: {{ en }}\n\nFrench:",
        "dataset_name": "opus_books",
        "dataset_config": "en-fr",
        "source_lang": "en",
        "target_lang": "fr",
    },
}


def get_task_definition(task_id: str) -> Dict[str, Any]:
    """Get built-in task definition by ID."""
    return BUILTIN_TASKS.get(task_id)


def list_builtin_tasks() -> list[str]:
    """List all built-in task IDs."""
    return list(BUILTIN_TASKS.keys())


def register_builtin_tasks():
    """Register all built-in tasks in the database."""
    from sqlalchemy.orm import Session
    from database import SessionLocal
    from models import Task, TaskType

    db = SessionLocal()
    try:
        for task_id, task_def in BUILTIN_TASKS.items():
            # Check if task already exists
            existing = db.query(Task).filter(Task.task_id == task_id).first()
            if existing:
                continue

            # Create new task
            task = Task(
                task_id=task_def["task_id"],
                name=task_def["name"],
                description=task_def.get("description"),
                task_type=TaskType(task_def["task_type"]),
                is_builtin=True,
                input_fields=task_def["input_fields"],
                label_field=task_def.get("label_field"),
                metrics=task_def["metrics"],
                prompt_template=task_def["prompt_template"],
                splits={"test": "builtin"},  # Placeholder
                golden_format=task_def.get("label_mapping"),
            )
            db.add(task)

        db.commit()
    finally:
        db.close()
