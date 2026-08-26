from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"
    required_role: str | None = None


class TaskUpdate(BaseModel):
    status: str | None = None
    assigned_agent_id: int | None = None
    priority: str | None = None
    required_role: str | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    description: str | None
    status: str
    priority: str
    assigned_agent_id: int | None
    required_role: str | None = None
    created_at: datetime
    updated_at: datetime