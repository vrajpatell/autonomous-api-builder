from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.domain.task_rules import (
    PROMPT_MAX_LENGTH,
    PROMPT_MIN_LENGTH,
    STATUS_MESSAGE_MAX_LENGTH,
    TITLE_MAX_LENGTH,
    TITLE_MIN_LENGTH,
)
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


class AgentRunRead(BaseModel):
    id: int
    orchestration_run_id: int
    task_id: int
    agent_name: str
    sequence: int
    status: str
    output_payload: str | None
    error_payload: str | None
    started_at: datetime | None
    completed_at: datetime | None

    class Config:
        from_attributes = True


class OrchestrationRunRead(BaseModel):
    id: int
    task_id: int
    status: str
    current_agent: str | None
    started_at: datetime
    completed_at: datetime | None
    agent_runs: list[AgentRunRead] = []

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str = Field(min_length=TITLE_MIN_LENGTH, max_length=TITLE_MAX_LENGTH)
    user_prompt: str = Field(min_length=PROMPT_MIN_LENGTH, max_length=PROMPT_MAX_LENGTH)

    @field_validator("title", "user_prompt")
    @classmethod
    def content_must_not_be_whitespace(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("content cannot be empty or whitespace-only")
        return stripped


class TaskStatusUpdate(BaseModel):
    status: TaskStatus
    message: str | None = Field(default=None, max_length=STATUS_MESSAGE_MAX_LENGTH)

    @field_validator("message")
    @classmethod
    def message_must_not_be_whitespace(cls, value: str | None) -> str | None:
        if value is None:
            return value
        stripped = value.strip()
        if not stripped:
            raise ValueError("message cannot be empty or whitespace-only")
        return stripped


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
    orchestration_runs: list[OrchestrationRunRead] = []
    agent_runs: list[AgentRunRead] = []

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
