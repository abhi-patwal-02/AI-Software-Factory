from typing import TypedDict, Any

from app.schemas.master_decision import MasterDecision


class FactoryState(TypedDict, total=False):

    project_id: int

    project_brain: dict[str, Any]

    decision: MasterDecision

    error: str | None