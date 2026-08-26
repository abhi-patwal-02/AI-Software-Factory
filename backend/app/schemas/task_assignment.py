from pydantic import BaseModel


class TaskAssignment(BaseModel):
    agent_id: int