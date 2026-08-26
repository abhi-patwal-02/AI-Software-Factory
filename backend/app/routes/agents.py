from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.agent import Agent
from app.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse
)


router = APIRouter(
    prefix="/agents",
    tags=["Agents"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=AgentResponse
)
def create_agent(
    agent: AgentCreate,
    db: Session = Depends(get_db)
):
    existing_agent = (
        db.query(Agent)
        .filter(Agent.name == agent.name)
        .first()
    )

    if existing_agent:
        raise HTTPException(
            status_code=409,
            detail="Agent already exists"
        )

    new_agent = Agent(
        name=agent.name,
        role=agent.role,
        description=agent.description
    )

    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)

    return new_agent


@router.get(
    "",
    response_model=list[AgentResponse]
)
def get_agents(
    db: Session = Depends(get_db)
):
    return db.query(Agent).all()


@router.get(
    "/{agent_id}",
    response_model=AgentResponse
)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db)
):
    agent = db.get(Agent, agent_id)

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    return agent


@router.patch(
    "/{agent_id}",
    response_model=AgentResponse
)
def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    db: Session = Depends(get_db)
):
    agent = db.get(Agent, agent_id)

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    if agent_update.status is not None:
        agent.status = agent_update.status

    db.commit()
    db.refresh(agent)

    return agent