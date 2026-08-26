from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LLMInteractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    agent_id: int | None
    provider: str
    model: str
    system_prompt: str | None
    input_context: dict | None
    raw_response: str | None
    parsed_decision: dict | None
    status: str
    error_message: str | None
    input_tokens: int | None
    output_tokens: int | None
    latency_ms: int | None
    created_at: datetime