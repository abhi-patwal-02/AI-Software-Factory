from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.project import Project
from app.schemas.project_brain import ProjectBrain
from app.services.project_brain import build_project_brain


router = APIRouter(
    prefix="/projects",
    tags=["Project Brain"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get(
    "/{project_id}/brain",
    response_model=ProjectBrain
)
def get_project_brain(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return build_project_brain(
        project_id,
        db
    )