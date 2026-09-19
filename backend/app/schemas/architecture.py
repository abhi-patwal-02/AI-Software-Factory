from pydantic import BaseModel, Field


class ArchitectureDecision(BaseModel):

    architecture: str = Field(
        description="High-level system architecture."
    )

    technology_stack: dict[str, str] = Field(
        description="Technology choices for the system."
    )

    components: list[str] = Field(
        description="Major system components."
    )

    system_boundaries: list[str] = Field(
        description="Major system boundaries and responsibilities."
    )

    technical_decisions: list[str] = Field(
        description="Important technical decisions and their rationale."
    )