from pydantic import BaseModel


class TaskDependencyCreate(BaseModel):
    depends_on_task_id: int


class TaskDependencyResponse(BaseModel):
    task_id: int
    depends_on_task_id: int