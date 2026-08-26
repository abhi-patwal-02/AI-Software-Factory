from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.error import Error
from app.models.task import Task
from app.schemas.master_decision import MasterDecision


def validate_master_decision(
    decision: MasterDecision,
    db: Session
) -> None:

    if decision.action == "wait":
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

        if task.status not in ["pending", "in_progress"]:
            raise ValueError(
                f"Task cannot be assigned from status '{task.status}'"
            )

        if agent.status != "idle":
            raise ValueError(
                "Agent is not idle"
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