from sqlalchemy.orm import Session, selectinload

from app.models.task import Task
from app.models.task_progress import TaskProgressUpdate
from app.models.task_status import TaskStatus
from app.queue import get_queue_backend
from app.schemas.task import TaskCreate


class TaskService:
    """Business logic for task creation and retrieval."""

    @staticmethod
    def create_task(db: Session, payload: TaskCreate) -> Task:
        task = Task(title=payload.title, user_prompt=payload.user_prompt, status=TaskStatus.pending.value)
        db.add(task)
        db.flush()
        db.add(
            TaskProgressUpdate(
                task_id=task.id,
                status=TaskStatus.pending.value,
                message="Task created and awaiting queue assignment",
            )
        )

        try:
            queue_backend = get_queue_backend()
            task.queue_job_id = queue_backend.enqueue_task_generation(task.id)
            task.status = TaskStatus.queued.value
            db.add(
                TaskProgressUpdate(
                    task_id=task.id,
                    status=TaskStatus.queued.value,
                    message="Task queued for asynchronous worker processing",
                )
            )
        except Exception as exc:
            task.status = TaskStatus.failed.value
            task.error_message = str(exc)
            db.add(
                TaskProgressUpdate(task_id=task.id, status=TaskStatus.failed.value, message=str(exc))
            )

        db.commit()
        db.refresh(task)
        return TaskService.get_task(db, task.id)

    @staticmethod
    def list_tasks(db: Session) -> list[Task]:
        return (
            db.query(Task)
            .options(
                selectinload(Task.plans),
                selectinload(Task.artifacts),
                selectinload(Task.progress_updates),
            )
            .order_by(Task.created_at.desc())
            .all()
        )

    @staticmethod
    def get_task(db: Session, task_id: int) -> Task | None:
        return (
            db.query(Task)
            .options(
                selectinload(Task.plans),
                selectinload(Task.artifacts),
                selectinload(Task.progress_updates),
            )
            .filter(Task.id == task_id)
            .first()
        )
