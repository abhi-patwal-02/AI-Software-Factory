from typing import Literal

from pydantic import BaseModel


class MasterDecision(BaseModel):
    action: Literal[
        "assign_task",
        "handle_error",
        "wait"
    ]

    task_id: int | None = None
    error_id: int | None = None
    agent_id: int | None = None

    reason: str