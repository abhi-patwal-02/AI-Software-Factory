from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.project import Project
from app.models.llm_interaction import LLMInteraction
from app.schemas.llm_interaction import LLMInteractionResponse


router = APIRouter(
    prefix="/llm-interactions",
    tags=["LLM Interactions"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get(
    "/projects/{project_id}",
    response_model=list[LLMInteractionResponse]
)
def get_project_llm_interactions(
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
        db.query(LLMInteraction)
        .filter(
            LLMInteraction.project_id == project_id
        )
        .order_by(LLMInteraction.id.desc())
        .all()
    )