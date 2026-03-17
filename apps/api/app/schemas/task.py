from datetime import datetime

from pydantic import BaseModel, Field

from app.models.task_status import TaskStatus


class TaskPlanRead(BaseModel):
    id: int
    step_number: int
    title: str
    description: str

    class Config:
        from_attributes = True


class GeneratedArtifactRead(BaseModel):
    id: int
    artifact_type: str
    file_name: str
    storage_backend: str
    storage_key: str
    content_type: str
    file_size: int
    created_at: datetime

    class Config:
        from_attributes = True


class TaskProgressUpdateRead(BaseModel):
    id: int
    status: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    user_prompt: str = Field(min_length=10)


class TaskStatusUpdate(BaseModel):
    status: TaskStatus
    message: str | None = Field(default=None, max_length=1000)


class TaskRead(BaseModel):
    id: int
    owner_id: int
    title: str
    user_prompt: str
    status: str
    queue_job_id: str | None
    error_message: str | None
    planner_status: str
    planner_source: str | None
    created_at: datetime
    updated_at: datetime | None
    plans: list[TaskPlanRead] = []
    artifacts: list[GeneratedArtifactRead] = []
    progress_updates: list[TaskProgressUpdateRead] = []

    class Config:
        from_attributes = True


class TaskListMeta(BaseModel):
    total_count: int
    current_page: int
    page_size: int
    total_pages: int


class PaginatedTaskRead(BaseModel):
    items: list[TaskRead]
    meta: TaskListMeta
