from pydantic import BaseModel


class TechnologyDecision(BaseModel):
    category: str
    technology: str
    reason: str


class TechnologyContract(BaseModel):
    decisions: list[TechnologyDecision]