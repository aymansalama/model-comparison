"""Upload API endpoints for custom tasks."""
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models import Task as DBTask
from schemas import UploadResponse
from upload_validator import UploadValidator
from config import settings

router = APIRouter()


@router.post("/tasks/upload", response_model=UploadResponse, status_code=201)
async def upload_custom_task(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a custom task.

    Accepts a ZIP file containing:
    - task.yaml: Task definition
    - Dataset files (JSONL or CSV)
    - Optional README.md

    Validates and registers the task.
    """
    validator = UploadValidator()

    # Save uploaded file
    upload_path = settings.UPLOAD_DIR / file.filename
    file_size = 0

    with open(upload_path, "wb") as f:
        content = await file.read()
        file_size = len(content)
        f.write(content)

    try:
        # Validate upload
        is_valid, error = validator.validate_upload(upload_path, file_size)
        if not is_valid:
            upload_path.unlink()
            raise HTTPException(status_code=400, detail=error)

        # Extract and validate task
        extract_dir = settings.CUSTOM_TASKS_DIR / upload_path.stem
        extract_dir.mkdir(parents=True, exist_ok=True)

        task_def, warnings, error = validator.extract_and_validate_task(
            upload_path, extract_dir
        )

        if error:
            # Clean up
            upload_path.unlink()
            import shutil

            shutil.rmtree(extract_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail=error)

        # Check if task_id is unique
        if not validator.check_task_id_unique(task_def.task_id, db):
            upload_path.unlink()
            import shutil

            shutil.rmtree(extract_dir, ignore_errors=True)
            raise HTTPException(
                status_code=400,
                detail=f"Task ID '{task_def.task_id}' already exists",
            )

        # Register task in database
        task = DBTask(
            task_id=task_def.task_id,
            name=task_def.name,
            description=task_def.description,
            task_type=task_def.task_type,
            is_builtin=False,
            input_fields=task_def.input_fields,
            label_field=task_def.label_field,
            schema=task_def.schema,
            metrics=task_def.metrics,
            prompt_template=task_def.prompt_template,
            splits=task_def.splits,
            golden_format=task_def.golden_format,
            storage_path=str(extract_dir),
        )

        db.add(task)
        db.commit()

        # Clean up upload file
        upload_path.unlink()

        return UploadResponse(
            task_id=task_def.task_id,
            message=f"Task '{task_def.name}' uploaded successfully",
            validation_warnings=warnings if warnings else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        if upload_path.exists():
            upload_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/tasks/{task_id}/test")
async def test_custom_task(
    task_id: str,
    model_id: str = "gpt-3.5-turbo",
    num_samples: int = 5,
    db: Session = Depends(get_db),
):
    """
    Test a custom task on a small sample.

    Args:
        task_id: Task identifier
        model_id: Model to use for testing
        num_samples: Number of samples to test (default 5)

    Runs the task on a few samples to verify it works.
    """
    # Verify task exists
    task = db.query(DBTask).filter(DBTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Import here to avoid circular dependency
    from benchmark_engine import BenchmarkEngine
    import asyncio

    try:
        # Create a mini benchmark run
        engine = BenchmarkEngine(db)

        # Run on limited samples
        result = await engine._evaluate_model_on_task(
            model_id=model_id,
            task_id=task_id,
            temperature=0.0,
            max_tokens=512,
            top_p=1.0,
            timeout=30,
            sample_cap=num_samples,
            trials=1,
            split="test",
            results_dir=settings.UPLOAD_DIR / f"test_{task_id}",
        )

        return {
            "status": "success",
            "task_id": task_id,
            "model_id": model_id,
            "num_samples": result.get("num_samples"),
            "metrics": result.get("metrics"),
            "num_errors": result.get("num_errors", 0),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")
