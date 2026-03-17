import logging
from dataclasses import dataclass
from datetime import datetime
from math import ceil

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from app.domain.task_workflow import InvalidTaskStatusTransitionError, TaskWorkflowPolicy
from app.models.artifact import GeneratedArtifact
from app.models.task import Task
from app.models.task_progress import TaskProgressUpdate
from app.models.task_status import TaskStatus
from app.observability import get_correlation_id
from app.observability.metrics import active_tasks, tasks_total
from app.queue import get_queue_backend
from app.schemas.task import PaginatedTaskRead, TaskCreate, TaskListMeta

logger = logging.getLogger(__name__)


@dataclass
class TaskListFilters:
    page: int = 1
    page_size: int = 10
    status: TaskStatus | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    search: str | None = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


class TaskService:
    """Business logic for task creation and retrieval."""

    @staticmethod
    def create_task(db: Session, payload: TaskCreate, owner_id: int) -> Task:
        task = Task(
            title=payload.title,
            user_prompt=payload.user_prompt,
            owner_id=owner_id,
            status=TaskStatus.pending.value,
            planner_status="pending",
        )
        db.add(task)
        db.flush()
        db.add(
            TaskProgressUpdate(
                task_id=task.id,
                status=TaskStatus.pending.value,
                message="Task created and awaiting queue assignment",
            )
        )
        tasks_total.labels(status=TaskStatus.pending.value).inc()
        active_tasks.inc()
        logger.info(
            "Task created",
            extra={"event": "task.created", "task_id": task.id, "owner_id": owner_id},
        )

        try:
            queue_backend = get_queue_backend()
            task.queue_job_id = queue_backend.enqueue_task_generation(task.id, correlation_id=get_correlation_id())
            TaskService.update_status(
                db,
                task,
                TaskStatus.queued,
                "Task queued for asynchronous worker processing",
                commit=False,
            )
            logger.info(
                "Task queued",
                extra={
                    "event": "task.queued",
                    "task_id": task.id,
                    "queue_job_id": task.queue_job_id,
                },
            )
        except Exception:
            task.error_message = "Task queue enqueue failure"
            TaskService.update_status(db, task, TaskStatus.failed, "Task queue enqueue failure", commit=False)
            logger.exception(
                "Failed to enqueue task",
                extra={"event": "task.enqueue_failed", "task_id": task.id},
            )

        db.commit()
        db.refresh(task)
        return TaskService.get_task(db, task.id, owner_id)

    @staticmethod
    def list_tasks(db: Session, owner_id: int, filters: TaskListFilters) -> PaginatedTaskRead:
        base_query = db.query(Task).filter(Task.owner_id == owner_id)

        if filters.status is not None:
            base_query = base_query.filter(Task.status == filters.status.value)
        if filters.date_from is not None:
            base_query = base_query.filter(Task.created_at >= filters.date_from)
        if filters.date_to is not None:
            base_query = base_query.filter(Task.created_at <= filters.date_to)
        if filters.search:
            needle = f"%{filters.search.lower()}%"
            base_query = base_query.filter(
                or_(
                    func.lower(Task.title).like(needle),
                    func.lower(Task.user_prompt).like(needle),
                )
            )

        total_count = base_query.count()
        total_pages = ceil(total_count / filters.page_size) if total_count else 0
        offset = (filters.page - 1) * filters.page_size

        sort_column = Task.created_at if filters.sort_by == "created_at" else Task.updated_at
        sort_direction = sort_column.desc() if filters.sort_order == "desc" else sort_column.asc()

        items = (
            base_query.options(
                selectinload(Task.plans),
                selectinload(Task.artifacts),
                selectinload(Task.progress_updates),
            )
            .order_by(sort_direction)
            .offset(offset)
            .limit(filters.page_size)
            .all()
        )

        return PaginatedTaskRead(
            items=items,
            meta=TaskListMeta(
                total_count=total_count,
                current_page=filters.page,
                page_size=filters.page_size,
                total_pages=total_pages,
            ),
        )

    @staticmethod
    def get_task(db: Session, task_id: int, owner_id: int) -> Task | None:
        return (
            db.query(Task)
            .options(
                selectinload(Task.plans),
                selectinload(Task.artifacts),
                selectinload(Task.progress_updates),
            )
            .filter(Task.id == task_id, Task.owner_id == owner_id)
            .first()
        )

    @staticmethod
    def list_artifacts(db: Session, task_id: int, owner_id: int) -> list[GeneratedArtifact] | None:
        task = db.query(Task.id).filter(Task.id == task_id, Task.owner_id == owner_id).first()
        if task is None:
            return None
        return (
            db.query(GeneratedArtifact)
            .filter(GeneratedArtifact.task_id == task_id)
            .order_by(GeneratedArtifact.created_at.desc())
            .all()
        )

    @staticmethod
    def get_artifact(db: Session, task_id: int, artifact_id: int, owner_id: int) -> GeneratedArtifact | None:
        return (
            db.query(GeneratedArtifact)
            .join(Task, Task.id == GeneratedArtifact.task_id)
            .filter(
                GeneratedArtifact.id == artifact_id,
                GeneratedArtifact.task_id == task_id,
                Task.owner_id == owner_id,
            )
            .first()
        )

    @staticmethod
    def update_task_status(
        db: Session,
        task_id: int,
        owner_id: int,
        next_status: TaskStatus,
        message: str | None = None,
    ) -> Task | None:
        task = TaskService.get_task(db, task_id, owner_id)
        if task is None:
            return None

        TaskService.update_status(db, task, next_status, message or f"Status changed to {next_status.value}")
        return TaskService.get_task(db, task.id, owner_id)

    @staticmethod
    def update_status(
        db: Session,
        task: Task,
        next_status: TaskStatus,
        message: str,
        *,
        commit: bool = True,
    ) -> None:
        current = TaskStatus(task.status)
        TaskWorkflowPolicy.validate_transition(current, next_status)

        task.status = next_status.value
        tasks_total.labels(status=next_status.value).inc()
        if next_status in {TaskStatus.completed, TaskStatus.failed, TaskStatus.cancelled}:
            active_tasks.dec()
        db.add(TaskProgressUpdate(task_id=task.id, status=next_status.value, message=message))
        logger.info(
            "Task status updated",
            extra={
                "event": "task.status_updated",
                "task_id": task.id,
                "from_status": current.value,
                "to_status": next_status.value,
                "message_text": message,
            },
        )
        if commit:
            db.commit()
            db.refresh(task)


__all__ = ["InvalidTaskStatusTransitionError"]
