from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.error import Error
from app.models.error_attempt import ErrorAttempt
from app.models.project import Project
from app.models.task import Task
from app.models.agent import Agent
from app.models.agent_run import AgentRun

from app.schemas.error import (
    ErrorCreate,
    ErrorUpdate,
    ErrorResponse
)

from app.schemas.error_attempt import (
    ErrorAttemptCreate,
    ErrorAttemptUpdate,
    ErrorAttemptResponse
)


router = APIRouter(
    prefix="/errors",
    tags=["Errors"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
        
@router.post(
    "",
    response_model=ErrorResponse
)
def create_error(
    error_data: ErrorCreate,
    db: Session = Depends(get_db)
):
    project = db.get(Project, error_data.project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    task = db.get(Task, error_data.task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    if task.project_id != error_data.project_id:
        raise HTTPException(
            status_code=400,
            detail="Task does not belong to this project"
        )

    error = Error(
        project_id=error_data.project_id,
        task_id=error_data.task_id,
        agent_run_id=error_data.agent_run_id,
        title=error_data.title,
        description=error_data.description,
        error_type=error_data.error_type,
        severity=error_data.severity,
        status="open"
    )

    db.add(error)
    db.commit()
    db.refresh(error)

    return error

@router.get(
    "/{error_id}",
    response_model=ErrorResponse
)
def get_error(
    error_id: int,
    db: Session = Depends(get_db)
):
    error = db.get(Error, error_id)

    if not error:
        raise HTTPException(
            status_code=404,
            detail="Error not found"
        )

    return error

@router.get(
    "/task/{task_id}",
    response_model=list[ErrorResponse]
)
def get_task_errors(
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
        db.query(Error)
        .filter(Error.task_id == task_id)
        .order_by(Error.id)
        .all()
    )
    
@router.patch(
    "/{error_id}",
    response_model=ErrorResponse
)
def update_error(
    error_id: int,
    error_update: ErrorUpdate,
    db: Session = Depends(get_db)
):
    error = db.get(Error, error_id)

    if not error:
        raise HTTPException(
            status_code=404,
            detail="Error not found"
        )

    if error_update.status is not None:
        error.status = error_update.status

    if error_update.root_cause is not None:
        error.root_cause = error_update.root_cause

    if error_update.resolution is not None:
        error.resolution = error_update.resolution

    if error_update.status == "resolved":
        error.resolved_at = datetime.utcnow()

        active_attempts = (
            db.query(ErrorAttempt)
            .filter(
                ErrorAttempt.error_id == error.id,
                ErrorAttempt.status == "in_progress"
            )
            .all()
        )

        for attempt in active_attempts:
            attempt.status = "completed"
            attempt.result = (
                attempt.result
                or "Error was resolved."
            )

    db.commit()
    db.refresh(error)

    return error

@router.post(
    "/{error_id}/attempts",
    response_model=ErrorAttemptResponse
)
def create_error_attempt(
    error_id: int,
    attempt_data: ErrorAttemptCreate,
    db: Session = Depends(get_db)
):
    error = db.get(Error, error_id)

    if not error:
        raise HTTPException(
            status_code=404,
            detail="Error not found"
        )

    agent = db.get(Agent, attempt_data.agent_id)

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
    
    if agent.role != "debugger":
        raise HTTPException(
            status_code=400,
            detail="Agent is not a debugging agent"
        )
        
    active_attempt = (
        db.query(ErrorAttempt)
        .filter(
            ErrorAttempt.error_id == error_id,
            ErrorAttempt.status == "in_progress"
        )
        .first()
    )

    if active_attempt:
        raise HTTPException(
            status_code=409,
            detail="This error already has an active debugging attempt"
        )

    last_attempt = (
        db.query(ErrorAttempt)
        .filter(ErrorAttempt.error_id == error_id)
        .order_by(ErrorAttempt.attempt_number.desc())
        .first()
    )

    attempt_number = (
        last_attempt.attempt_number + 1
        if last_attempt
        else 1
    )

    attempt = ErrorAttempt(
        error_id=error_id,
        agent_id=attempt_data.agent_id,
        attempt_number=attempt_number,
        diagnosis=attempt_data.diagnosis,
        action_taken=attempt_data.action_taken,
        status="in_progress"
    )
    
    agent.status = "working"

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt

@router.patch(
    "/attempts/{attempt_id}",
    response_model=ErrorAttemptResponse
)
def update_error_attempt(
    attempt_id: int,
    attempt_update: ErrorAttemptUpdate,
    db: Session = Depends(get_db)
):
    attempt = db.get(ErrorAttempt, attempt_id)

    if not attempt:
        raise HTTPException(
            status_code=404,
            detail="Error attempt not found"
        )

    if attempt_update.result is not None:
        attempt.result = attempt_update.result

    if attempt_update.status is not None:

        if attempt_update.status not in [
            "in_progress",
            "completed",
            "failed"
        ]:
            raise HTTPException(
                status_code=400,
                detail="Invalid error attempt status"
            )

        attempt.status = attempt_update.status

        if attempt_update.status in ["completed", "failed"]:
            agent = db.get(Agent, attempt.agent_id)

            if agent:
                other_active_attempt = (
                    db.query(ErrorAttempt)
                    .filter(
                        ErrorAttempt.agent_id == agent.id,
                        ErrorAttempt.status == "in_progress",
                        ErrorAttempt.id != attempt.id
                    )
                    .first()
                )

                active_run = (
                    db.query(AgentRun)
                    .filter(
                        AgentRun.agent_id == agent.id,
                        AgentRun.status == "running"
                    )
                    .first()
                )

                if not other_active_attempt and not active_run:
                    agent.status = "idle"

    db.commit()
    db.refresh(attempt)

    return attempt

@router.get(
    "/{error_id}/attempts",
    response_model=list[ErrorAttemptResponse]
)
def get_error_attempts(
    error_id: int,
    db: Session = Depends(get_db)
):
    error = db.get(Error, error_id)

    if not error:
        raise HTTPException(
            status_code=404,
            detail="Error not found"
        )

    return (
        db.query(ErrorAttempt)
        .filter(ErrorAttempt.error_id == error_id)
        .order_by(ErrorAttempt.attempt_number)
        .all()
    )