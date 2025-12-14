"""API routers."""
from .models import router as models_router
from .tasks import router as tasks_router
from .runs import router as runs_router
from .uploads import router as uploads_router

__all__ = ["models_router", "tasks_router", "runs_router", "uploads_router"]
