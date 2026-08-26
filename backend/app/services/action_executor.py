from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.error import Error
from app.models.error_attempt import ErrorAttempt
from app.models.task import Task
from app.models.agent_run import AgentRun

from app.schemas.master_decision import MasterDecision


def execute_master_decision(
    decision: MasterDecision,
    db: Session
):
    if decision.action == "wait":
        return {
            "action": "wait",
            "status": "no_action"
        }

    if decision.action == "assign_task":
        return execute_assign_task(
            decision,
            db
        )

    if decision.action == "handle_error":
        return execute_handle_error(
            decision,
            db
        )

    raise ValueError(
        f"Unsupported action: {decision.action}"
    )
    
def execute_assign_task(
    decision: MasterDecision,
    db: Session
):
    task = db.get(Task, decision.task_id)

    if not task:
        raise ValueError("Task not found")

    agent = db.get(Agent, decision.agent_id)

    if not agent:
        raise ValueError("Agent not found")

    if agent.status != "idle":
        raise ValueError("Agent is not available")

    if task.status not in ["pending", "in_progress"]:
        raise ValueError(
            f"Task cannot be assigned from status '{task.status}'"
        )

    if task.assigned_agent_id is not None:
        raise ValueError(
            "Task is already assigned to an agent"
        )

    active_run = (
        db.query(AgentRun)
        .filter(
            AgentRun.task_id == task.id,
            AgentRun.status == "running"
        )
        .first()
    )

    if active_run:
        raise ValueError(
            "Task already has an active agent run"
        )

    task.assigned_agent_id = agent.id
    task.status = "in_progress"

    agent.status = "working"

    run = AgentRun(
        agent_id=agent.id,
        task_id=task.id,
        status="running",
        input_context=task.description
    )

    db.add(run)

    db.commit()
    db.refresh(run)

    return {
        "action": "assign_task",
        "status": "executed",
        "task_id": task.id,
        "agent_id": agent.id,
        "agent_run_id": run.id
    }
    
def execute_handle_error(
    decision: MasterDecision,
    db: Session
):
    error = db.get(Error, decision.error_id)

    if not error:
        raise ValueError("Error not found")

    agent = db.get(Agent, decision.agent_id)

    if not agent:
        raise ValueError("Agent not found")
    
    if agent.status != "idle":
        raise ValueError("Agent is not available")

    if agent.role != "debugger":
        raise ValueError("Agent is not a debugging agent")

    if error.status != "open":
        raise ValueError(
            f"Error cannot be handled from status '{error.status}'"
        )

    active_attempt = (
        db.query(ErrorAttempt)
        .filter(
            ErrorAttempt.error_id == error.id,
            ErrorAttempt.status == "in_progress"
        )
        .first()
    )

    if active_attempt:
        raise ValueError(
            "Error already has an active debugging attempt"
        )

    last_attempt = (
        db.query(ErrorAttempt)
        .filter(
            ErrorAttempt.error_id == error.id
        )
        .order_by(
            ErrorAttempt.attempt_number.desc()
        )
        .first()
    )

    attempt_number = (
        last_attempt.attempt_number + 1
        if last_attempt
        else 1
    )

    attempt = ErrorAttempt(
        error_id=error.id,
        agent_id=agent.id,
        attempt_number=attempt_number,
        diagnosis=(
            "Error assigned to debugging agent "
            "for investigation."
        ),
        action_taken=(
            "Inspect the failed run, project context, "
            "and identify the root cause."
        ),
        status="in_progress"
    )

    agent.status = "working"

    db.add(attempt)

    db.commit()
    db.refresh(attempt)

    return {
        "action": "handle_error",
        "status": "executed",
        "error_id": error.id,
        "agent_id": agent.id,
        "attempt_id": attempt.id
    }