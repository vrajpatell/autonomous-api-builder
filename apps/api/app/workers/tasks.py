import logging
import time

from opentelemetry import trace

from app.db.session import SessionLocal
from app.domain.task_workflow import InvalidTaskStatusTransitionError
from app.models.task import Task
from app.models.task_progress import TaskProgressUpdate
from app.models.task_status import TaskStatus
from app.observability import new_id, set_request_context
from app.observability.metrics import worker_job_duration_seconds, worker_jobs_total
from app.services.orchestration_service import OrchestrationService
from app.services.task_service import TaskService
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


@celery_app.task(name="app.workers.process_generation_task")
def process_generation_task(task_id: int, correlation_id: str | None = None) -> None:
    set_request_context(request_id=new_id(), correlation_id=correlation_id or new_id())
    started = time.perf_counter()

    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            logger.warning("Worker received unknown task", extra={"event": "worker.task_missing", "task_id": task_id})
            return
        logger.info(
            "Worker started task",
            extra={"event": "worker.task_started", "task_id": task_id, "queue_job_id": task.queue_job_id},
        )
        with tracer.start_as_current_span("worker.process_generation_task", attributes={"task.id": task_id}):
            OrchestrationService.run(db, task)
        worker_jobs_total.labels(result="success").inc()
    except Exception:
        worker_jobs_total.labels(result="failure").inc()
        task = db.query(Task).filter(Task.id == task_id).first()
        if task is not None:
            task.planner_status = "failed"
            task.error_message = "Background worker execution failed"
            try:
                TaskService.update_status(
                    db,
                    task,
                    TaskStatus.failed,
                    "Background worker execution failed",
                    commit=False,
                )
            except InvalidTaskStatusTransitionError:
                db.add(
                    TaskProgressUpdate(
                        task_id=task.id,
                        status=task.status,
                        message="Worker encountered terminal failure",
                    )
                )
            db.commit()
        logger.exception("Worker task failed", extra={"event": "worker.task_failed", "task_id": task_id})
        raise
    finally:
        worker_job_duration_seconds.observe(time.perf_counter() - started)
        db.close()
