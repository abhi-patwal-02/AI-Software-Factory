from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ErrorAttemptCreate(BaseModel):
    agent_id: int
    diagnosis: str
    action_taken: str


class ErrorAttemptUpdate(BaseModel):
    result: str | None = None
    status: str | None = None


class ErrorAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    error_id: int
    agent_id: int
    attempt_number: int
    diagnosis: str
    action_taken: str
    result: str | None
    status: str
    created_at: datetime