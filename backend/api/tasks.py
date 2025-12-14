"""Tasks API endpoints."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Task as DBTask
from schemas import TaskResponse

router = APIRouter()


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    """
    List all available tasks.

    Args:
        include_inactive: Include inactive tasks in results

    Returns list of tasks (both built-in and custom).
    """
    query = db.query(DBTask)

    if not include_inactive:
        query = query.filter(DBTask.is_active == True)

    tasks = query.all()
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """
    Get task details by ID.

    Args:
        task_id: Task identifier

    Returns task information.
    """
    task = db.query(DBTask).filter(DBTask.task_id == task_id).first()
    if not task:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return task
