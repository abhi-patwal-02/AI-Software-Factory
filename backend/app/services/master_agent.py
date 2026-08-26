from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.error import Error
from app.models.task import Task
from app.models.task_dependency import TaskDependency
from app.models.error_attempt import ErrorAttempt

from app.schemas.master_decision import MasterDecision

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

def decide_next_action(
    project_id: int,
    db: Session
) -> MasterDecision:

    # 1. Handle actionable open errors first

    open_errors = (
        db.query(Error)
        .filter(
            Error.project_id == project_id,
            Error.status == "open"
        )
        .order_by(Error.id)
        .all()
    )

    error = None

    for candidate in open_errors:

        active_attempt = (
            db.query(ErrorAttempt)
            .filter(
                ErrorAttempt.error_id == candidate.id,
                ErrorAttempt.status == "in_progress"
            )
            .first()
        )

        if active_attempt:
            continue

        error = candidate
        break

    if error:

        debugger = (
            db.query(Agent)
            .filter(
                Agent.role == "debugger",
                Agent.status == "idle"
            )
            .first()
        )

        if debugger:

            return MasterDecision(
                action="handle_error",
                error_id=error.id,
                agent_id=debugger.id,
                reason=(
                    "An open error without an active attempt "
                    "exists and a debugging agent is available."
                )
            )

    # 2. Find the highest-priority ready task

    pending_tasks = (
        db.query(Task)
        .filter(
            Task.project_id == project_id,
            Task.status == "pending",
            Task.assigned_agent_id.is_(None)
        )
        .order_by(Task.priority.desc())
        .all()
    )

    task = None

    for candidate in pending_tasks:

        if dependencies_satisfied(
            candidate,
            db
        ):
            task = candidate
            break

    if task:

        agent_query = (
            db.query(Agent)
            .filter(
                Agent.status == "idle",
                Agent.role != "orchestrator"
            )
        )

        if task.required_role:
            agent_query = agent_query.filter(
                Agent.role == task.required_role
            )

        agent = agent_query.first()

        if agent:

            return MasterDecision(
                action="assign_task",
                task_id=task.id,
                agent_id=agent.id,
                reason=(
                    "A pending task exists and an idle "
                    "compatible agent is available."
                )
            )

    # 3. Nothing to do

    return MasterDecision(
        action="wait",
        reason="No actionable work is currently available."
    )