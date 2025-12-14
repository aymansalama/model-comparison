"""Benchmark execution engine."""
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session

from models import Task, Model, Run, Result, RunStatus
from providers import ProviderClient, OpenAIClient, BedrockClient
from tasks import TaskLoader
from metrics import MetricsCalculator
from config import settings


class BenchmarkEngine:
    """Execute benchmark runs across models and tasks."""

    def __init__(self, db: Session):
        """
        Initialize benchmark engine.

        Args:
            db: Database session
        """
        self.db = db
        self.task_loader = TaskLoader()
        self.metrics_calculator = MetricsCalculator()
        self.providers: Dict[str, ProviderClient] = {}

        # Initialize providers
        try:
            if settings.OPENAI_API_KEY:
                self.providers["openai"] = OpenAIClient()
        except Exception as e:
            print(f"Failed to initialize OpenAI client: {e}")

        try:
            self.providers["bedrock"] = BedrockClient()
        except Exception as e:
            print(f"Failed to initialize Bedrock client: {e}")

    async def execute_run(self, run_id: str) -> None:
        """
        Execute a benchmark run.

        Args:
            run_id: Run ID
        """
        # Load run from database
        run = self.db.query(Run).filter(Run.run_id == run_id).first()
        if not run:
            raise ValueError(f"Run {run_id} not found")

        try:
            # Update run status
            run.status = RunStatus.RUNNING
            run.started_at = datetime.utcnow()
            self.db.commit()

            # Load configuration
            config = run.config
            temperature = config.get("temperature", settings.DEFAULT_TEMPERATURE)
            max_tokens = config.get("max_tokens", settings.DEFAULT_MAX_TOKENS)
            top_p = config.get("top_p", settings.DEFAULT_TOP_P)
            timeout = config.get("timeout", settings.DEFAULT_TIMEOUT)
            sample_cap = config.get("sample_cap", settings.DEFAULT_SAMPLE_CAP)
            trials = config.get("trials", settings.DEFAULT_TRIALS)
            split = config.get("split", "test")

            # Create results directory
            results_dir = settings.RESULTS_DIR / run_id
            results_dir.mkdir(parents=True, exist_ok=True)
            run.results_path = str(results_dir)

            # Calculate total evaluations
            total_evals = len(run.selected_models) * len(run.selected_tasks)
            run.total_evaluations = total_evals
            self.db.commit()

            # Execute evaluations
            completed = 0
            failed = 0

            for model_id in run.selected_models:
                for task_id in run.selected_tasks:
                    try:
                        # Run evaluation
                        result = await self._evaluate_model_on_task(
                            model_id=model_id,
                            task_id=task_id,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            top_p=top_p,
                            timeout=timeout,
                            sample_cap=sample_cap,
                            trials=trials,
                            split=split,
                            results_dir=results_dir,
                        )

                        # Save result to database
                        db_result = Result(
                            run_id=run.id,
                            task_id=task_id,
                            model_id=model_id,
                            metrics=result["metrics"],
                            avg_latency_ms=result.get("avg_latency_ms"),
                            p50_latency_ms=result.get("p50_latency_ms"),
                            p95_latency_ms=result.get("p95_latency_ms"),
                            p99_latency_ms=result.get("p99_latency_ms"),
                            total_input_tokens=result.get("total_input_tokens"),
                            total_output_tokens=result.get("total_output_tokens"),
                            estimated_cost_usd=result.get("estimated_cost_usd"),
                            num_samples=result.get("num_samples"),
                            num_errors=result.get("num_errors", 0),
                            raw_outputs_path=result.get("raw_outputs_path"),
                            metrics_path=result.get("metrics_path"),
                        )
                        self.db.add(db_result)
                        completed += 1

                    except Exception as e:
                        print(f"Error evaluating {model_id} on {task_id}: {e}")
                        failed += 1

                    # Update progress
                    run.completed_evaluations = completed
                    run.failed_evaluations = failed
                    run.progress_percent = (completed + failed) / total_evals * 100
                    self.db.commit()

            # Generate aggregated reports
            self._generate_leaderboard(run, results_dir)
            self._generate_manifest(run, results_dir)

            # Mark run as completed
            run.status = RunStatus.COMPLETED
            run.completed_at = datetime.utcnow()
            self.db.commit()

        except Exception as e:
            # Mark run as failed
            run.status = RunStatus.FAILED
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
            self.db.commit()
            raise

    async def _evaluate_model_on_task(
        self,
        model_id: str,
        task_id: str,
        temperature: float,
        max_tokens: int,
        top_p: float,
        timeout: int,
        sample_cap: Optional[int],
        trials: int,
        split: str,
        results_dir: Path,
    ) -> Dict[str, Any]:
        """Evaluate a single model on a single task."""
        # Load task
        task = self.db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Load model
        model = self.db.query(Model).filter(Model.model_id == model_id).first()
        if not model:
            raise ValueError(f"Model {model_id} not found")

        # Get provider client
        provider_client = self.providers.get(model.provider)
        if not provider_client:
            raise ValueError(f"Provider {model.provider} not available")

        # Load dataset
        if task.is_builtin:
            dataset = self.task_loader.load_builtin_dataset(task_id, split, sample_cap)
        else:
            # Load custom dataset
            dataset_path = Path(task.storage_path) / task.splits.get(split, "")
            dataset = self.task_loader.load_custom_dataset(
                task_id, dataset_path, split, sample_cap
            )

        # Run inference on all samples
        predictions = []
        references = []
        latencies = []
        input_tokens_list = []
        output_tokens_list = []
        raw_outputs = []
        num_errors = 0

        for sample in dataset:
            # Prepare prompt
            prompt = self.task_loader.prepare_prompt(task.prompt_template, sample)

            # Extract reference
            reference = self.task_loader.extract_label(
                sample, task.label_field, task.task_type.value, task.golden_format
            )

            # Run multiple trials if specified
            trial_predictions = []
            trial_latencies = []

            for _ in range(trials):
                try:
                    # Generate response
                    response = await provider_client.generate(
                        prompt=prompt,
                        model_id=model_id,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        timeout=timeout,
                    )

                    # Parse output
                    prediction = self.task_loader.parse_model_output(
                        response.text, task.task_type.value
                    )

                    trial_predictions.append(prediction)
                    trial_latencies.append(response.latency_ms)

                    if response.input_tokens:
                        input_tokens_list.append(response.input_tokens)
                    if response.output_tokens:
                        output_tokens_list.append(response.output_tokens)

                except Exception as e:
                    print(f"Error generating response: {e}")
                    num_errors += 1
                    trial_predictions.append(None)
                    trial_latencies.append(None)

            # Use first successful prediction (or majority vote for multiple trials)
            prediction = next((p for p in trial_predictions if p is not None), None)
            if prediction is not None:
                predictions.append(prediction)
                references.append(reference)

                # Average latency across trials
                valid_latencies = [l for l in trial_latencies if l is not None]
                if valid_latencies:
                    latencies.append(np.mean(valid_latencies))

                # Store raw output
                raw_outputs.append({
                    "sample": sample,
                    "prompt": prompt,
                    "prediction": prediction,
                    "reference": reference,
                    "latency_ms": latencies[-1] if latencies else None,
                })

        # Calculate metrics
        metrics = {}
        if predictions and references:
            metrics = self.metrics_calculator.calculate_metrics(
                predictions, references, task.metrics, task.task_type.value
            )

        # Calculate performance statistics
        result = {
            "metrics": metrics,
            "num_samples": len(dataset),
            "num_errors": num_errors,
        }

        if latencies:
            result["avg_latency_ms"] = float(np.mean(latencies))
            result["p50_latency_ms"] = float(np.percentile(latencies, 50))
            result["p95_latency_ms"] = float(np.percentile(latencies, 95))
            result["p99_latency_ms"] = float(np.percentile(latencies, 99))

        if input_tokens_list:
            result["total_input_tokens"] = sum(input_tokens_list)
        if output_tokens_list:
            result["total_output_tokens"] = sum(output_tokens_list)

        # Calculate estimated cost
        if model_id in settings.MODEL_PRICING:
            pricing = settings.MODEL_PRICING[model_id]
            input_cost = (result.get("total_input_tokens", 0) / 1000) * pricing["input"]
            output_cost = (result.get("total_output_tokens", 0) / 1000) * pricing["output"]
            result["estimated_cost_usd"] = input_cost + output_cost

        # Save raw outputs
        raw_outputs_path = results_dir / f"{task_id}_{model_id}_outputs.jsonl"
        with open(raw_outputs_path, "w", encoding="utf-8") as f:
            for output in raw_outputs:
                f.write(json.dumps(output) + "\n")
        result["raw_outputs_path"] = str(raw_outputs_path)

        # Save metrics
        metrics_path = results_dir / f"{task_id}_{model_id}_metrics.json"
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        result["metrics_path"] = str(metrics_path)

        return result

    def _generate_leaderboard(self, run: Run, results_dir: Path) -> None:
        """Generate leaderboard CSV."""
        results = self.db.query(Result).filter(Result.run_id == run.id).all()

        leaderboard_data = []
        for result in results:
            row = {
                "model_id": result.model_id,
                "task_id": result.task_id,
                **result.metrics,
                "avg_latency_ms": result.avg_latency_ms,
                "estimated_cost_usd": result.estimated_cost_usd,
            }
            leaderboard_data.append(row)

        # Save as CSV
        import pandas as pd

        df = pd.DataFrame(leaderboard_data)
        leaderboard_path = results_dir / "leaderboard.csv"
        df.to_csv(leaderboard_path, index=False)

    def _generate_manifest(self, run: Run, results_dir: Path) -> None:
        """Generate run manifest."""
        manifest = {
            "run_id": run.run_id,
            "name": run.name,
            "created_at": run.created_at.isoformat(),
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "status": run.status.value,
            "config": run.config,
            "models": run.selected_models,
            "tasks": run.selected_tasks,
            "total_evaluations": run.total_evaluations,
            "completed_evaluations": run.completed_evaluations,
            "failed_evaluations": run.failed_evaluations,
        }

        manifest_path = results_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
