from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_run import AgentRun
from app.models.error import Error
from app.models.error_attempt import ErrorAttempt


def handle_failed_run(
    run_id: int,
    db: Session
):
    """
    Handle a failed agent run.

    Responsibilities:
    1. Find the failed agent run.
    2. Find the error associated with that run.
    3. Find an available debugging agent.
    4. Mark the debugging agent as working.
    5. Create the first error attempt.
    """

    run = db.get(AgentRun, run_id)

    if not run:
        return None

    if run.status != "failed":
        return None

    error = (
        db.query(Error)
        .filter(Error.agent_run_id == run_id)
        .first()
    )

    if not error:
        return None

    debugging_agent = (
        db.query(Agent)
        .filter(
            Agent.role == "debugger",
            Agent.status == "idle"
        )
        .first()
    )

    if not debugging_agent:
        return None

    debugging_agent.status = "working"

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
        agent_id=debugging_agent.id,
        attempt_number=attempt_number,
        diagnosis=(
            "Agent execution failed. "
            "Root cause analysis is required."
        ),
        action_taken=(
            "Inspect the failed agent run, "
            "project context, and task requirements."
        ),
        status="in_progress"
    )

    db.add(attempt)

    return attempt