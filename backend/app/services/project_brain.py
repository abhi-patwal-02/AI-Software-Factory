from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.task import Task
from app.models.task_dependency import TaskDependency
from app.models.agent import Agent
from app.models.agent_run import AgentRun
from app.models.error import Error
from app.models.error_attempt import ErrorAttempt

from app.schemas.project_brain import ProjectBrain


def build_project_brain(
    project_id: int,
    db: Session
) -> ProjectBrain:

    project = db.get(Project, project_id)

    if not project:
        raise ValueError("Project not found")

    tasks = (
        db.query(Task)
        .filter(Task.project_id == project_id)
        .all()
    )

    dependencies = (
        db.query(TaskDependency)
        .join(
            Task,
            TaskDependency.task_id == Task.id
        )
        .filter(Task.project_id == project_id)
        .all()
    )

    agents = db.query(Agent).all()

    task_ids = [task.id for task in tasks]

    runs = []

    if task_ids:
        runs = (
            db.query(AgentRun)
            .filter(
                AgentRun.task_id.in_(task_ids)
            )
            .order_by(AgentRun.id.desc())
            .all()
        )

    errors = []

    if task_ids:
        errors = (
            db.query(Error)
            .filter(
                Error.task_id.in_(task_ids)
            )
            .order_by(Error.id.desc())
            .all()
        )
        
    error_ids = [error.id for error in errors]

    error_attempts = []

    if error_ids:
        error_attempts = (
            db.query(ErrorAttempt)
            .filter(
                ErrorAttempt.error_id.in_(error_ids)
            )
            .order_by(ErrorAttempt.id.desc())
            .all()
        )
        
    active_task_by_agent = {
        run.agent_id: run.task_id
        for run in runs
        if run.status == "running"
    }

    active_error_by_agent = {
        attempt.agent_id: attempt.error_id
        for attempt in error_attempts
        if attempt.status == "in_progress"
    }

    brain = ProjectBrain(
        project={
            "id": project.id,
            "name": project.name,
            "description": project.description
        },

        tasks={
            "pending": [
                task_to_dict(task)
                for task in tasks
                if task.status == "pending"
            ],

            "in_progress": [
                task_to_dict(task)
                for task in tasks
                if task.status == "in_progress"
            ],

            "completed": [
                task_to_dict(task)
                for task in tasks
                if task.status == "completed"
            ],

            "failed": [
                task_to_dict(task)
                for task in tasks
                if task.status == "failed"
            ],

            "blocked": [
                task_to_dict(task)
                for task in tasks
                if task.status == "blocked"
            ]
        },

        dependencies=[
            {
                "task_id": dependency.task_id,
                "depends_on_task_id": dependency.depends_on_task_id
            }
            for dependency in dependencies
        ],

        agents={
            "idle": [
                agent_to_dict(
                    agent,
                    active_task_by_agent.get(agent.id),
                    active_error_by_agent.get(agent.id)
                )
                for agent in agents
                if agent.status == "idle"
            ],

            "working": [
                agent_to_dict(
                    agent,
                    active_task_by_agent.get(agent.id),
                    active_error_by_agent.get(agent.id)
                )
                for agent in agents
                if agent.status == "working"
            ],

            "failed": [
                agent_to_dict(
                    agent,
                    active_task_by_agent.get(agent.id),
                    active_error_by_agent.get(agent.id)
                )
                for agent in agents
                if agent.status == "failed"
            ]
        },

        active_runs=[
            run_to_dict(run)
            for run in runs
            if run.status == "running"
        ],

        recent_runs=[
            run_to_dict(run)
            for run in runs[:20]
        ],

        active_errors=[
            error_to_dict(error)
            for error in errors
            if error.status == "open"
        ],

        error_history=[
            error_to_dict(error)
            for error in errors[:20]
        ],
        
        active_error_attempts=[
            error_attempt_to_dict(attempt)
            for attempt in error_attempts
            if attempt.status == "in_progress"
        ],

        recent_error_attempts=[
            error_attempt_to_dict(attempt)
            for attempt in error_attempts[:20]
        ],

        decisions=[],

        current_focus=None
    )

    return brain

def task_to_dict(task: Task) -> dict:
    return {
        "id": task.id,
        "project_id": task.project_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "assigned_agent_id": task.assigned_agent_id,
        "required_role": task.required_role
    }


def agent_to_dict(
    agent: Agent,
    current_task_id: int | None = None,
    current_error_id: int | None = None
) -> dict:

    return {
        "id": agent.id,
        "name": agent.name,
        "role": agent.role,
        "description": agent.description,
        "status": agent.status,
        "current_task_id": current_task_id,
        "current_error_id": current_error_id
    }


def run_to_dict(run: AgentRun) -> dict:
    return {
        "id": run.id,
        "agent_id": run.agent_id,
        "task_id": run.task_id,
        "status": run.status,
        "input_context": run.input_context,
        "output_summary": run.output_summary,
        "started_at": run.started_at,
        "completed_at": run.completed_at
    }


def error_to_dict(error: Error) -> dict:
    return {
        "id": error.id,
        "project_id": error.project_id,
        "task_id": error.task_id,
        "agent_run_id": error.agent_run_id,
        "title": error.title,
        "description": error.description,
        "error_type": error.error_type,
        "severity": error.severity,
        "status": error.status,
        "root_cause": error.root_cause,
        "resolution": error.resolution,
        "created_at": error.created_at,
        "resolved_at": error.resolved_at
    }
    
def error_attempt_to_dict(
    attempt: ErrorAttempt
) -> dict:

    return {
        "id": attempt.id,
        "error_id": attempt.error_id,
        "agent_id": attempt.agent_id,
        "attempt_number": attempt.attempt_number,
        "diagnosis": attempt.diagnosis,
        "action_taken": attempt.action_taken,
        "result": attempt.result,
        "status": attempt.status,
        "created_at": attempt.created_at
    }