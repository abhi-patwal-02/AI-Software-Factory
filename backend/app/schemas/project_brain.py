from typing import Any

from pydantic import BaseModel


class ProjectBrain(BaseModel):
    project: dict[str, Any]

    tasks: dict[str, list[dict[str, Any]]]

    dependencies: list[dict[str, Any]]

    agents: dict[str, list[dict[str, Any]]]

    active_runs: list[dict[str, Any]]

    recent_runs: list[dict[str, Any]]

    active_errors: list[dict[str, Any]]

    error_history: list[dict[str, Any]]

    active_error_attempts: list[dict[str, Any]]

    recent_error_attempts: list[dict[str, Any]]

    decisions: list[dict[str, Any]]

    current_focus: dict[str, Any] | None = None