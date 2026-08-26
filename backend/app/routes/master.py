from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.master_agent import decide_next_action
from app.schemas.master_decision import MasterDecision
from app.services.master_decision import validate_master_decision
from app.services.action_executor import execute_master_decision


router = APIRouter(
    prefix="/projects",
    tags=["Master Agent"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get(
    "/{project_id}/master/decision",
    response_model=MasterDecision
)
def get_master_decision(
    project_id: int,
    db: Session = Depends(get_db)
):
    return decide_next_action(
        project_id,
        db
    )
    
@router.post(
    "/{project_id}/master/execute",
)
def execute_master_action(
    project_id: int,
    db: Session = Depends(get_db)
):
    decision = decide_next_action(
        project_id,
        db
    )

    try:
        validate_master_decision(
            decision,
            db
        )

        result = execute_master_decision(
            decision,
            db
        )

        return {
            "decision": decision,
            "execution": result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )