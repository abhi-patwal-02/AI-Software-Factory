from app.database import SessionLocal
from app.models.task import Task
from app.services.llm.openrouter_provider import OpenRouterProvider
from app.schemas.architecture import ArchitectureDecision
from app.services.agents.architect_prompt import (
    ARCHITECT_SYSTEM_PROMPT
)


db = SessionLocal()

try:

    task = db.get(
        Task,
        13
    )

    if not task:
        raise ValueError(
            "Task 13 not found"
        )

    provider = OpenRouterProvider()

    input_context = {
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
        }
    }

    print("\n===== ARCHITECT LLM TEST =====")
    print("Model:", provider.model)

    result = provider.generate(
        system_prompt=ARCHITECT_SYSTEM_PROMPT,
        input_context=input_context,
        response_model=ArchitectureDecision
    )

    print("\n===== RAW RESPONSE =====")
    print(result["raw_response"])

    print("\n===== PARSED ARCHITECTURE =====")

    architecture = ArchitectureDecision.model_validate_json(
        result["raw_response"]
    )

    print(
        architecture.model_dump_json(
            indent=2
        )
    )

finally:
    db.close()