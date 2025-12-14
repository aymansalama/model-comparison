"""Celery application and tasks."""
import asyncio
from celery import Celery
from config import settings
from database import SessionLocal
from benchmark_engine import BenchmarkEngine

# Create Celery app
celery_app = Celery(
    "benchmark_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, name="run_benchmark")
def run_benchmark(self, run_id: str):
    """
    Celery task to run a benchmark.

    Args:
        run_id: Run ID to execute
    """
    db = SessionLocal()
    try:
        # Create engine
        engine = BenchmarkEngine(db)

        # Execute run
        asyncio.run(engine.execute_run(run_id))

        return {"status": "completed", "run_id": run_id}

    except Exception as e:
        # Update run status to failed
        from models import Run, RunStatus
        from datetime import datetime

        run = db.query(Run).filter(Run.run_id == run_id).first()
        if run:
            run.status = RunStatus.FAILED
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
            db.commit()

        raise

    finally:
        db.close()


@celery_app.task(name="test_task")
def test_task():
    """Test task to verify Celery is working."""
    return {"status": "ok", "message": "Celery is working!"}
