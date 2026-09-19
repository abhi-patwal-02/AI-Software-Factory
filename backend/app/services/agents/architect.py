from sqlalchemy.orm import Session

from app.models.task import Task
from app.services.agents.base import AgentRunner
from app.services.agents.architect_prompt import (
    ARCHITECT_SYSTEM_PROMPT
)
from app.services.llm.openrouter_provider import OpenRouterProvider
from app.schemas.architecture import ArchitectureDecision


class ArchitectAgent(AgentRunner):

    def run(
        self,
        task: Task,
        db: Session
    ) -> str:

        provider = OpenRouterProvider()

        input_context = {
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
            }
        }

        result = provider.generate(
            system_prompt=ARCHITECT_SYSTEM_PROMPT,
            input_context=input_context,
            response_model=ArchitectureDecision
        )

        architecture = ArchitectureDecision.model_validate_json(
            result["raw_response"]
        )

        return architecture.model_dump_json(
            indent=2
        )