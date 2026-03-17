from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.task_status import TaskStatus
from app.models.user import User
from app.schemas.task import GeneratedArtifactRead, PaginatedTaskRead, TaskCreate, TaskRead, TaskStatusUpdate
from app.services.artifact_storage import get_artifact_storage
from app.services.task_service import InvalidTaskStatusTransitionError, TaskListFilters, TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=201)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    return TaskService.create_task(db, payload, current_user.id)


@router.get("", response_model=PaginatedTaskRead)
def list_tasks(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    status: TaskStatus | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=255),
    sort_by: Literal["created_at", "updated_at"] = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedTaskRead:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from must be before or equal to date_to")

    filters = TaskListFilters(
        page=page,
        page_size=page_size,
        status=status,
        date_from=date_from,
        date_to=date_to,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return TaskService.list_tasks(db, current_user.id, filters)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TaskRead:
    task = TaskService.get_task(db, task_id, current_user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/{task_id}/artifacts", response_model=list[GeneratedArtifactRead])
def list_task_artifacts(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[GeneratedArtifactRead]:
    artifacts = TaskService.list_artifacts(db, task_id, current_user.id)
    if artifacts is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return artifacts


@router.get("/{task_id}/artifacts/{artifact_id}", response_model=GeneratedArtifactRead)
def get_task_artifact_metadata(
    task_id: int,
    artifact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GeneratedArtifactRead:
    artifact = TaskService.get_artifact(db, task_id, artifact_id, current_user.id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact


@router.get("/{task_id}/artifacts/{artifact_id}/download")
def download_task_artifact(
    task_id: int,
    artifact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    artifact = TaskService.get_artifact(db, task_id, artifact_id, current_user.id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")

    storage = get_artifact_storage()
    try:
        content = storage.read_bytes(artifact.storage_key)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Artifact file not found") from exc

    return Response(
        content=content,
        media_type=artifact.content_type,
        headers={"Content-Disposition": f'attachment; filename="{artifact.file_name}"'},
    )


@router.patch("/{task_id}/status", response_model=TaskRead)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    try:
        task = TaskService.update_task_status(
            db,
            task_id,
            current_user.id,
            payload.status,
            payload.message,
        )
    except InvalidTaskStatusTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
