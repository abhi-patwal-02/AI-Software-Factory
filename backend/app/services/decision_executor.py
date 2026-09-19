from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.task import Task
from app.schemas.master_decision import MasterDecision


def execute_decision(
    decision: MasterDecision,
    db: Session
) -> None:

    if decision.action == "wait":
        return

    if decision.action == "assign_task":

        task = db.get(
            Task,
            decision.task_id
        )

        agent = db.get(
            Agent,
            decision.agent_id
        )

        if not task:
            raise ValueError(
                "Task not found during execution"
            )

        if not agent:
            raise ValueError(
                "Agent not found during execution"
            )

        task.status = "in_progress"
        task.assigned_agent_id = agent.id

        agent.status = "working"

        db.commit()

        return

    if decision.action == "handle_error":
        raise NotImplementedError(
            "handle_error execution is not implemented yet"
        )

    raise ValueError(
        f"Unsupported decision action: {decision.action}"
    )