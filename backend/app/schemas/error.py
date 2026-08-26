from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ErrorCreate(BaseModel):
    project_id: int
    task_id: int
    agent_run_id: int | None = None
    title: str
    description: str
    error_type: str
    severity: str


class ErrorUpdate(BaseModel):
    status: str | None = None
    root_cause: str | None = None
    resolution: str | None = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    task_id: int
    agent_run_id: int | None
    title: str
    description: str
    error_type: str
    severity: str
    status: str
    root_cause: str | None
    resolution: str | None
    created_at: datetime
    resolved_at: datetime | None