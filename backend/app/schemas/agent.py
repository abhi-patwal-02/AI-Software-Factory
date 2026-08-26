from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AgentCreate(BaseModel):
    name: str
    role: str
    description: str | None = None


class AgentUpdate(BaseModel):
    status: str | None = None


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    role: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime