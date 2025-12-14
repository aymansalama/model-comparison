"""Runs API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from database import get_db
from models import Run as DBRun, RunStatus, Result as DBResult, Task as DBTask, Model as DBModel
from schemas import (
    RunCreate,
    RunResponse,
    RunDetailResponse,
    ResultResponse,
    LeaderboardEntry,
)
from celery_app import run_benchmark

router = APIRouter()


@router.post("/runs", response_model=RunResponse, status_code=201)
async def create_run(run_data: RunCreate, db: Session = Depends(get_db)):
    """
    Create a new benchmark run.

    Validates selected models and tasks, creates run record, and queues execution.
    """
    # Validate models exist
    for model_id in run_data.model_ids:
        model = db.query(DBModel).filter(DBModel.model_id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")

    # Validate tasks exist
    for task_id in run_data.task_ids:
        task = db.query(DBTask).filter(DBTask.task_id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Generate run ID
    run_id = f"run_{uuid.uuid4().hex[:12]}"

    # Create run
    run = DBRun(
        run_id=run_id,
        name=run_data.name or f"Run {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        description=run_data.description,
        status=RunStatus.QUEUED,
        config=run_data.config.model_dump(),
        selected_models=run_data.model_ids,
        selected_tasks=run_data.task_ids,
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    # Queue benchmark execution
    task = run_benchmark.delay(run_id)
    run.celery_task_id = task.id
    db.commit()

    return run


@router.get("/runs", response_model=List[RunResponse])
async def list_runs(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    List benchmark runs.

    Args:
        status: Filter by status (queued, running, completed, failed)
        limit: Maximum number of results
        offset: Pagination offset

    Returns list of runs ordered by creation date (newest first).
    """
    query = db.query(DBRun).order_by(DBRun.created_at.desc())

    if status:
        try:
            status_enum = RunStatus(status)
            query = query.filter(DBRun.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    query = query.limit(limit).offset(offset)
    runs = query.all()

    return runs


@router.get("/runs/{run_id}", response_model=RunDetailResponse)
async def get_run(run_id: str, db: Session = Depends(get_db)):
    """
    Get run details and progress.

    Args:
        run_id: Run identifier

    Returns detailed run information including progress.
    """
    run = db.query(DBRun).filter(DBRun.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    return run


@router.get("/runs/{run_id}/results", response_model=List[ResultResponse])
async def get_run_results(run_id: str, db: Session = Depends(get_db)):
    """
    Get results for a run.

    Args:
        run_id: Run identifier

    Returns list of results for each model-task combination.
    """
    # Verify run exists
    run = db.query(DBRun).filter(DBRun.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    # Get results
    results = db.query(DBResult).filter(DBResult.run_id == run.id).all()

    return results


@router.get("/runs/{run_id}/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(run_id: str, db: Session = Depends(get_db)):
    """
    Get leaderboard for a run.

    Args:
        run_id: Run identifier

    Returns leaderboard entries sorted by performance.
    """
    # Verify run exists
    run = db.query(DBRun).filter(DBRun.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    # Get results
    results = db.query(DBResult).filter(DBResult.run_id == run.id).all()

    # Convert to leaderboard entries
    entries = []
    for result in results:
        entry = LeaderboardEntry(
            model_id=result.model_id,
            task_id=result.task_id,
            metrics=result.metrics,
            avg_latency_ms=result.avg_latency_ms,
            estimated_cost_usd=result.estimated_cost_usd,
        )
        entries.append(entry)

    return entries


@router.get("/runs/{run_id}/logs")
async def get_run_logs(run_id: str, db: Session = Depends(get_db)):
    """
    Get logs for a run.

    Args:
        run_id: Run identifier

    Returns run logs (if available).
    """
    run = db.query(DBRun).filter(DBRun.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    # For now, return basic status info
    # In production, this would read from log files
    logs = {
        "run_id": run_id,
        "status": run.status.value,
        "progress": f"{run.completed_evaluations}/{run.total_evaluations}",
        "error_message": run.error_message,
    }

    return logs


@router.get("/exports/{run_id}.csv")
async def export_results_csv(run_id: str, db: Session = Depends(get_db)):
    """
    Export run results as CSV.

    Args:
        run_id: Run identifier

    Returns CSV file with results.
    """
    from pathlib import Path

    run = db.query(DBRun).filter(DBRun.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    if not run.results_path:
        raise HTTPException(status_code=404, detail="Results not available yet")

    leaderboard_path = Path(run.results_path) / "leaderboard.csv"
    if not leaderboard_path.exists():
        raise HTTPException(status_code=404, detail="Leaderboard file not found")

    return FileResponse(
        path=leaderboard_path,
        media_type="text/csv",
        filename=f"{run_id}_results.csv",
    )


@router.delete("/runs/{run_id}", status_code=204)
async def delete_run(run_id: str, db: Session = Depends(get_db)):
    """
    Delete a run.

    Args:
        run_id: Run identifier
    """
    run = db.query(DBRun).filter(DBRun.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    # Only allow deletion of completed or failed runs
    if run.status in [RunStatus.QUEUED, RunStatus.RUNNING]:
        raise HTTPException(
            status_code=400, detail="Cannot delete running or queued runs"
        )

    db.delete(run)
    db.commit()

    return None
