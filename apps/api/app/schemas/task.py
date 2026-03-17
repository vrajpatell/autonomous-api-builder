from datetime import datetime

from pydantic import BaseModel, Field


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
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    user_prompt: str = Field(min_length=10)


class TaskRead(BaseModel):
    id: int
    title: str
    user_prompt: str
    status: str
    created_at: datetime
    updated_at: datetime | None
    plans: list[TaskPlanRead] = []
    artifacts: list[GeneratedArtifactRead] = []

    class Config:
        from_attributes = True
