from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.error import Error
from app.models.task import Task
from app.schemas.master_decision import MasterDecision
from app.models.task_dependency import TaskDependency

def dependencies_satisfied(
    task: Task,
    db: Session
) -> bool:

    dependencies = (
        db.query(TaskDependency)
        .filter(
            TaskDependency.task_id == task.id
        )
        .all()
    )

    for dependency in dependencies:

        dependency_task = db.get(
            Task,
            dependency.depends_on_task_id
        )

        if not dependency_task:
            return False

        if dependency_task.status != "completed":
            return False

    return True

def validate_master_decision(
    decision: MasterDecision,
    db: Session
) -> None:

    if decision.action == "wait":

        if decision.task_id is not None:
            raise ValueError(
                "wait decision cannot contain task_id"
            )

        if decision.error_id is not None:
            raise ValueError(
                "wait decision cannot contain error_id"
            )

        if decision.agent_id is not None:
            raise ValueError(
                "wait decision cannot contain agent_id"
            )

        return

    if decision.action == "assign_task":

        if decision.task_id is None:
            raise ValueError(
                "task_id is required for assign_task"
            )

        if decision.agent_id is None:
            raise ValueError(
                "agent_id is required for assign_task"
            )

        task = db.get(Task, decision.task_id)

        if not task:
            raise ValueError(
                "Task not found"
            )

        agent = db.get(Agent, decision.agent_id)

        if not agent:
            raise ValueError(
                "Agent not found"
            )

        if task.status != "pending":
            raise ValueError(
                f"Task cannot be assigned from status '{task.status}'"
            )

        if task.assigned_agent_id is not None:
            raise ValueError(
                "Task is already assigned to an agent"
            )

        if agent.status != "idle":
            raise ValueError(
                "Agent is not idle"
            )
        
        if not dependencies_satisfied(
            task,
            db
        ):
            raise ValueError(
                "Task dependencies are not satisfied"
            )
        
        if (
            task.required_role
            and agent.role != task.required_role
        ):
            raise ValueError(
                f"Agent role '{agent.role}' does not match "
                f"required role '{task.required_role}'"
            )

        return

    if decision.action == "handle_error":

        if decision.error_id is None:
            raise ValueError(
                "error_id is required for handle_error"
            )

        if decision.agent_id is None:
            raise ValueError(
                "agent_id is required for handle_error"
            )

        error = db.get(Error, decision.error_id)

        if not error:
            raise ValueError(
                "Error not found"
            )

        agent = db.get(Agent, decision.agent_id)

        if not agent:
            raise ValueError(
                "Agent not found"
            )

        if error.status != "open":
            raise ValueError(
                f"Error is not open: {error.status}"
            )

        if agent.role != "debugger":
            raise ValueError(
                "Selected agent is not a debugging agent"
            )

        if agent.status != "idle":
            raise ValueError(
                "Debugging agent is not idle"
            )

        return