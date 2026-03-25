from pydantic import BaseModel, Field


class ApiError(BaseModel):
    code: str = Field(description="Machine-readable error code")
    message: str
    details: dict | None = None


class ApiErrorResponse(BaseModel):
    error: ApiError
