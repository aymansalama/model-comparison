"""Metrics calculator for NLP tasks."""
import re
import json
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from scipy.stats import pearsonr, spearmanr
from rouge_score import rouge_scorer
from sacrebleu import BLEU, CHRF
from seqeval.metrics import f1_score as ner_f1_score
from seqeval.metrics import precision_score as ner_precision
from seqeval.metrics import recall_score as ner_recall


class MetricsCalculator:
    """Calculate metrics for various NLP tasks."""

    def __init__(self):
        """Initialize metrics calculator."""
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ["rouge1", "rouge2", "rougeL"], use_stemmer=True
        )
        self.bleu_scorer = BLEU()
        self.chrf_scorer = CHRF()

    def calculate_metrics(
        self,
        predictions: List[Any],
        references: List[Any],
        metric_names: List[str],
        task_type: str,
    ) -> Dict[str, float]:
        """
        Calculate specified metrics.

        Args:
            predictions: Model predictions
            references: Ground truth references
            metric_names: List of metric names to calculate
            task_type: Type of task

        Returns:
            Dictionary of metric names to values
        """
        results = {}

        for metric_name in metric_names:
            try:
                value = self._calculate_single_metric(
                    predictions, references, metric_name, task_type
                )
                results[metric_name] = value
            except Exception as e:
                print(f"Error calculating {metric_name}: {e}")
                results[metric_name] = 0.0

        return results

    def _calculate_single_metric(
        self,
        predictions: List[Any],
        references: List[Any],
        metric_name: str,
        task_type: str,
    ) -> float:
        """Calculate a single metric."""
        metric_name_lower = metric_name.lower()

        # Classification metrics
        if metric_name_lower == "accuracy":
            return self._accuracy(predictions, references)
        elif metric_name_lower == "f1" or metric_name_lower == "f1_macro":
            return self._f1_macro(predictions, references)
        elif metric_name_lower == "f1_micro":
            return self._f1_micro(predictions, references)
        elif metric_name_lower == "f1_weighted":
            return self._f1_weighted(predictions, references)
        elif metric_name_lower == "precision":
            return self._precision(predictions, references)
        elif metric_name_lower == "recall":
            return self._recall(predictions, references)

        # NER metrics
        elif metric_name_lower == "ner_f1":
            return self._ner_f1(predictions, references)
        elif metric_name_lower == "ner_precision":
            return self._ner_precision(predictions, references)
        elif metric_name_lower == "ner_recall":
            return self._ner_recall(predictions, references)

        # ROUGE metrics
        elif metric_name_lower == "rouge1":
            return self._rouge1(predictions, references)
        elif metric_name_lower == "rouge2":
            return self._rouge2(predictions, references)
        elif metric_name_lower == "rougel":
            return self._rougeL(predictions, references)

        # BLEU metrics
        elif metric_name_lower == "bleu":
            return self._bleu(predictions, references)
        elif metric_name_lower == "chrf":
            return self._chrf(predictions, references)

        # QA metrics
        elif metric_name_lower == "exact_match" or metric_name_lower == "em":
            return self._exact_match(predictions, references)
        elif metric_name_lower == "f1_qa":
            return self._f1_qa(predictions, references)

        # Similarity metrics
        elif metric_name_lower == "pearson":
            return self._pearson(predictions, references)
        elif metric_name_lower == "spearman":
            return self._spearman(predictions, references)

        else:
            raise ValueError(f"Unknown metric: {metric_name}")

    # Classification metrics
    def _accuracy(self, predictions: List[str], references: List[str]) -> float:
        """Calculate accuracy."""
        return float(accuracy_score(references, predictions))

    def _f1_macro(self, predictions: List[str], references: List[str]) -> float:
        """Calculate macro F1 score."""
        return float(f1_score(references, predictions, average="macro", zero_division=0))

    def _f1_micro(self, predictions: List[str], references: List[str]) -> float:
        """Calculate micro F1 score."""
        return float(f1_score(references, predictions, average="micro", zero_division=0))

    def _f1_weighted(self, predictions: List[str], references: List[str]) -> float:
        """Calculate weighted F1 score."""
        return float(f1_score(references, predictions, average="weighted", zero_division=0))

    def _precision(self, predictions: List[str], references: List[str]) -> float:
        """Calculate precision."""
        return float(precision_score(references, predictions, average="macro", zero_division=0))

    def _recall(self, predictions: List[str], references: List[str]) -> float:
        """Calculate recall."""
        return float(recall_score(references, predictions, average="macro", zero_division=0))

    # NER metrics
    def _ner_f1(self, predictions: List[List[str]], references: List[List[str]]) -> float:
        """Calculate NER F1 score."""
        return float(ner_f1_score(references, predictions))

    def _ner_precision(self, predictions: List[List[str]], references: List[List[str]]) -> float:
        """Calculate NER precision."""
        return float(ner_precision(references, predictions))

    def _ner_recall(self, predictions: List[List[str]], references: List[List[str]]) -> float:
        """Calculate NER recall."""
        return float(ner_recall(references, predictions))

    # ROUGE metrics
    def _rouge1(self, predictions: List[str], references: List[str]) -> float:
        """Calculate ROUGE-1 F1 score."""
        scores = []
        for pred, ref in zip(predictions, references):
            score = self.rouge_scorer.score(ref, pred)
            scores.append(score["rouge1"].fmeasure)
        return float(np.mean(scores))

    def _rouge2(self, predictions: List[str], references: List[str]) -> float:
        """Calculate ROUGE-2 F1 score."""
        scores = []
        for pred, ref in zip(predictions, references):
            score = self.rouge_scorer.score(ref, pred)
            scores.append(score["rouge2"].fmeasure)
        return float(np.mean(scores))

    def _rougeL(self, predictions: List[str], references: List[str]) -> float:
        """Calculate ROUGE-L F1 score."""
        scores = []
        for pred, ref in zip(predictions, references):
            score = self.rouge_scorer.score(ref, pred)
            scores.append(score["rougeL"].fmeasure)
        return float(np.mean(scores))

    # BLEU metrics
    def _bleu(self, predictions: List[str], references: List[str]) -> float:
        """Calculate BLEU score."""
        # sacrebleu expects references as list of lists
        refs = [[ref] for ref in references]
        score = self.bleu_scorer.corpus_score(predictions, list(zip(*refs)))
        return float(score.score / 100.0)  # Normalize to 0-1

    def _chrf(self, predictions: List[str], references: List[str]) -> float:
        """Calculate ChrF score."""
        refs = [[ref] for ref in references]
        score = self.chrf_scorer.corpus_score(predictions, list(zip(*refs)))
        return float(score.score / 100.0)  # Normalize to 0-1

    # QA metrics
    def _exact_match(self, predictions: List[str], references: List[str]) -> float:
        """Calculate exact match score for QA."""
        matches = []
        for pred, ref in zip(predictions, references):
            pred_normalized = self._normalize_answer(pred)
            ref_normalized = self._normalize_answer(ref)
            matches.append(pred_normalized == ref_normalized)
        return float(np.mean(matches))

    def _f1_qa(self, predictions: List[str], references: List[str]) -> float:
        """Calculate token-level F1 score for QA."""
        f1_scores = []
        for pred, ref in zip(predictions, references):
            pred_tokens = self._normalize_answer(pred).split()
            ref_tokens = self._normalize_answer(ref).split()

            if len(ref_tokens) == 0:
                f1_scores.append(1.0 if len(pred_tokens) == 0 else 0.0)
                continue

            common_tokens = set(pred_tokens) & set(ref_tokens)
            if len(common_tokens) == 0:
                f1_scores.append(0.0)
                continue

            precision = len(common_tokens) / len(pred_tokens) if pred_tokens else 0
            recall = len(common_tokens) / len(ref_tokens)
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            f1_scores.append(f1)

        return float(np.mean(f1_scores))

    def _normalize_answer(self, text: str) -> str:
        """Normalize answer for QA evaluation."""
        # Remove articles, punctuation, and extra whitespace
        text = text.lower()
        text = re.sub(r"\b(a|an|the)\b", " ", text)
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # Similarity metrics
    def _pearson(self, predictions: List[float], references: List[float]) -> float:
        """Calculate Pearson correlation."""
        if len(predictions) < 2:
            return 0.0
        corr, _ = pearsonr(predictions, references)
        return float(corr) if not np.isnan(corr) else 0.0

    def _spearman(self, predictions: List[float], references: List[float]) -> float:
        """Calculate Spearman correlation."""
        if len(predictions) < 2:
            return 0.0
        corr, _ = spearmanr(predictions, references)
        return float(corr) if not np.isnan(corr) else 0.0
