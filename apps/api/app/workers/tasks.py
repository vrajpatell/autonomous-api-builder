from app.db.session import SessionLocal
from app.domain.task_workflow import InvalidTaskStatusTransitionError
from app.models.task import Task
from app.models.task_progress import TaskProgressUpdate
from app.models.task_status import TaskStatus
from app.services.generation_pipeline import GenerationPipeline
from app.services.task_service import TaskService
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.process_generation_task")
def process_generation_task(task_id: int) -> None:
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            return
        GenerationPipeline.run(db, task)
    except Exception as exc:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task is not None:
            task.planner_status = "failed"
            task.error_message = str(exc)
            try:
                TaskService.update_status(db, task, TaskStatus.failed, str(exc), commit=False)
            except InvalidTaskStatusTransitionError:
                db.add(TaskProgressUpdate(task_id=task.id, status=task.status, message=f"Worker error: {exc}"))
            db.commit()
        raise
    finally:
        db.close()
