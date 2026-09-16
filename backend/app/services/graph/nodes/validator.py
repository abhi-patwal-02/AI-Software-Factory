from sqlalchemy.orm import Session

from app.schemas.master_decision import MasterDecision
from app.services.master_decision import validate_master_decision
from app.services.graph.state import FactoryState


def validate_decision_node(
    state: FactoryState,
    db: Session
) -> FactoryState:

    decision = MasterDecision.model_validate(
        state["decision"]
    )

    validate_master_decision(
        decision,
        db
    )

    return {
        "validation_error": None
    }