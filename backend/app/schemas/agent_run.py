from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AgentRunCreate(BaseModel):
    input_context: str | None = None


class AgentRunUpdate(BaseModel):
    status: str
    output_summary: str | None = None


class AgentRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_id: int
    task_id: int
    status: str
    input_context: str | None
    output_summary: str | None
    started_at: datetime
    completed_at: datetime | None