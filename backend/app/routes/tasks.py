from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.project import Project
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.models.task_dependency import TaskDependency
from app.schemas.task_dependency import (
    TaskDependencyCreate,
    TaskDependencyResponse
)
from app.models.agent import Agent
from app.schemas.task_assignment import TaskAssignment

from sqlalchemy import exists, select
from sqlalchemy.orm import Session, aliased


router = APIRouter(
    tags=["Tasks"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskResponse
)
def create_task(
    project_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    new_task = Task(
        project_id=project_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        required_role=task.required_role
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get(
    "/projects/{project_id}/tasks",
    response_model=list[TaskResponse]
)
def get_tasks(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return (
        db.query(Task)
        .filter(Task.project_id == project_id)
        .all()
    )

@router.post(
    "/tasks/{task_id}/dependencies",
    response_model=TaskDependencyResponse
)
def add_task_dependency(
    task_id: int,
    dependency: TaskDependencyCreate,
    db: Session = Depends(get_db)
):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    dependency_task = db.get(
        Task,
        dependency.depends_on_task_id
    )

    if not dependency_task:
        raise HTTPException(
            status_code=404,
            detail="Dependency task not found"
        )

    if task_id == dependency.depends_on_task_id:
        raise HTTPException(
            status_code=400,
            detail="A task cannot depend on itself"
        )

    existing_dependency = (
        db.query(TaskDependency)
        .filter(
            TaskDependency.task_id == task_id,
            TaskDependency.depends_on_task_id
            == dependency.depends_on_task_id
        )
        .first()
    )

    if existing_dependency:
        raise HTTPException(
            status_code=409,
            detail="Dependency already exists"
        )

    new_dependency = TaskDependency(
        task_id=task_id,
        depends_on_task_id=dependency.depends_on_task_id
    )

    db.add(new_dependency)
    db.commit()
    db.refresh(new_dependency)

    return new_dependency

@router.get(
    "/tasks/{task_id}/dependencies",
    response_model=list[TaskDependencyResponse]
)
def get_task_dependencies(
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
        db.query(TaskDependency)
        .filter(TaskDependency.task_id == task_id)
        .all()
    )
    
@router.get(
    "/projects/{project_id}/tasks/ready",
    response_model=list[TaskResponse]
)
def get_ready_tasks(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    dependency_task = aliased(Task)

    incomplete_dependency = (
        select(TaskDependency.task_id)
        .join(
            dependency_task,
            dependency_task.id == TaskDependency.depends_on_task_id
        )
        .where(
            TaskDependency.task_id == Task.id,
            dependency_task.status != "completed"
        )
        .correlate(Task)
    )

    query = (
        select(Task)
        .where(
            Task.project_id == project_id,
            Task.status == "pending",
            ~exists(incomplete_dependency)
        )
    )

    result = db.execute(query)

    return result.scalars().all()

@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    if task_update.status is not None:
        task.status = task_update.status

    if task_update.assigned_agent_id is not None:
        task.assigned_agent_id = task_update.assigned_agent_id

    if task_update.priority is not None:
        task.priority = task_update.priority
        
    if task_update.required_role is not None:
        task.required_role = task_update.required_role

    db.commit()
    db.refresh(task)

    return task

@router.post(
    "/tasks/{task_id}/assign",
    response_model=TaskResponse
)
def assign_task(
    task_id: int,
    assignment: TaskAssignment,
    db: Session = Depends(get_db)
):
    task = db.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    agent = db.get(Agent, assignment.agent_id)

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

    task.assigned_agent_id = agent.id

    db.commit()
    db.refresh(task)

    return task