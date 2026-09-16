from typing import Literal

from pydantic import BaseModel, Field


class MasterDecision(BaseModel):
    action: Literal[
        "assign_task",
        "handle_error",
        "wait"
    ] = Field(
        description="The action the Master Agent should take."
    )

    task_id: int | None = Field(
        default=None,
        description="Required when action is assign_task. ID of the task to assign."
    )

    error_id: int | None = Field(
        default=None,
        description="Required when action is handle_error. ID of the error to handle."
    )

    agent_id: int | None = Field(
        default=None,
        description="Required when action is assign_task or handle_error. ID of the agent."
    )

    reason: str = Field(
        description="Concise explanation for the decision."
    )