from typing import Any, TypedDict


class FactoryState(TypedDict, total=False):

    project_id: int

    project_brain: dict[str, Any]

    decision: dict[str, Any] | None

    validation_error: str | None