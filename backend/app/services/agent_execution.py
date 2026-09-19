from datetime import datetime

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_run import AgentRun
from app.models.task import Task
from app.services.agents.factory import get_agent_runner


def execute_agent_task(
    task: Task,
    agent: Agent,
    db: Session
) -> str:

    if task.status != "in_progress":
        raise ValueError(
            f"Task cannot be executed from status "
            f"'{task.status}'"
        )

    if task.assigned_agent_id != agent.id:
        raise ValueError(
            "Task is not assigned to this agent"
        )

    if agent.status != "working":
        raise ValueError(
            f"Agent cannot execute task from status "
            f"'{agent.status}'"
        )

    runner = get_agent_runner(agent)

    agent_run = AgentRun(
        agent_id=agent.id,
        task_id=task.id,
        status="running",
        input_context=task.description,
        started_at=datetime.utcnow()
    )

    db.add(agent_run)
    db.commit()
    db.refresh(agent_run)

    try:

        result = runner.run(
            task,
            db
        )

        agent_run.status = "completed"
        agent_run.output_summary = result
        agent_run.completed_at = datetime.utcnow()

        task.status = "completed"
        agent.status = "idle"

        db.commit()

        return result

    except Exception as exc:

        agent_run.status = "failed"
        agent_run.output_summary = None
        agent_run.completed_at = datetime.utcnow()

        task.status = "failed"
        agent.status = "idle"

        db.commit()

        raise exc