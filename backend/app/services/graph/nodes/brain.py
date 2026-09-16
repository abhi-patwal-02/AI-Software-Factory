from sqlalchemy.orm import Session

from app.services.project_brain import build_project_brain
from app.services.graph.state import FactoryState


def build_brain_node(
    state: FactoryState,
    db: Session
) -> FactoryState:

    brain = build_project_brain(
        state["project_id"],
        db
    )

    return {
        "project_brain": brain.model_dump(
            mode="json"
        )
    }