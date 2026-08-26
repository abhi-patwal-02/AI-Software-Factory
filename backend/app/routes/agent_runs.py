from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.agent import Agent
from app.models.agent_run import AgentRun
from app.models.task import Task
from app.schemas.agent_run import (
    AgentRunCreate,
    AgentRunUpdate,
    AgentRunResponse
)
from app.models.error import Error
from app.services.orchestrator import handle_failed_run


router = APIRouter(
    prefix="/agent-runs",
    tags=["Agent Runs"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/tasks/{task_id}/agents/{agent_id}",
    response_model=AgentRunResponse
)
def start_agent_run(
    task_id: int,
    agent_id: int,
    run_data: AgentRunCreate,
    db: Session = Depends(get_db)
):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    agent = db.get(Agent, agent_id)

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    if agent.status != "idle":
        raise HTTPException(
            status_code=409,
            detail="Agent is not available"
        )

    if task.assigned_agent_id != agent_id:
        raise HTTPException(
            status_code=409,
            detail="Agent is not assigned to this task"
        )

    if task.status not in ["pending", "in_progress"]:
        raise HTTPException(
            status_code=409,
            detail=f"Task cannot be started from status '{task.status}'"
        )

    active_run = (
        db.query(AgentRun)
        .filter(
            AgentRun.task_id == task_id,
            AgentRun.status == "running"
        )
        .first()
    )

    if active_run:
        raise HTTPException(
            status_code=409,
            detail="Task already has an active agent run"
        )

    run = AgentRun(
        agent_id=agent_id,
        task_id=task_id,
        status="running",
        input_context=run_data.input_context
    )

    task.status = "in_progress"
    agent.status = "working"

    db.add(run)
    db.commit()
    db.refresh(run)

    return run


@router.patch(
    "/{run_id}",
    response_model=AgentRunResponse
)
def update_agent_run(
    run_id: int,
    run_update: AgentRunUpdate,
    db: Session = Depends(get_db)
):
    run = db.get(AgentRun, run_id)

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Agent run not found"
        )
        
    if run_update.status not in ["running", "completed", "failed"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid agent run status"
        )
        
    if run.status in ["completed", "failed"]:
        raise HTTPException(
            status_code=409,
            detail=f"Agent run is already {run.status}"
        )

    run.status = run_update.status

    if run_update.output_summary is not None:
        run.output_summary = run_update.output_summary

    if run_update.status in ["completed", "failed"]:
        run.completed_at = datetime.utcnow()

        agent = db.get(Agent, run.agent_id)

        if agent:
            agent.status = "idle"

        task = db.get(Task, run.task_id)

        if task:
            if run_update.status == "completed":
                task.status = "completed"
            elif run_update.status == "failed":
                task.status = "failed"
                
                error = Error(
                project_id=task.project_id,
                task_id=task.id,
                agent_run_id=run.id,
                title=f"Agent run {run.id} failed",
                description=(
                    run.output_summary
                    or "Agent execution failed without a detailed summary."
                ),
                error_type="AgentExecutionError",
                severity="high",
                status="open"
                )
                
                db.add(error)
                
                db.flush()
                    
                handle_failed_run(
                    run_id=run.id,
                    db=db
                )

    db.commit()
    db.refresh(run)

    return run


@router.get(
    "/tasks/{task_id}",
    response_model=list[AgentRunResponse]
)
def get_task_runs(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return (
        db.query(AgentRun)
        .filter(AgentRun.task_id == task_id)
        .order_by(AgentRun.id)
        .all()
    )