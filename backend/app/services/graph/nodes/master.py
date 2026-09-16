from sqlalchemy.orm import Session

from app.schemas.master_decision import MasterDecision
from app.services.llm.openrouter_provider import OpenRouterProvider
from app.services.graph.state import FactoryState


MASTER_AGENT_PROMPT = """
You are the Master Agent of an autonomous AI Software Factory.

Your job is to decide the next action for the project based on the
provided Project Brain.

You may choose exactly one action:

1. assign_task
   Assign a pending, ready task to a compatible idle agent.

2. handle_error
   Assign an open error without an active attempt to an idle debugger.

3. wait
   Choose this when no safe actionable work is available.

Rules:

- Only use task, error, and agent IDs that exist in the Project Brain.
- Do not assign completed or failed tasks.
- Do not assign a task whose dependencies are incomplete.
- Do not assign a task to a non-idle agent.
- Respect required_role when selecting an agent.
- Only debugging agents may handle errors.
- Do not handle an error that already has an in-progress attempt.
- Prefer actionable errors before new tasks.
- If no safe action is available, choose wait.
- Do not execute the action yourself.

Return ONLY one JSON object.

Always include:
- action
- task_id
- error_id
- agent_id
- reason

For assign_task:
- task_id is required
- agent_id is required
- error_id must be null

For handle_error:
- error_id is required
- agent_id is required
- task_id must be null

For wait:
- task_id must be null
- error_id must be null
- agent_id must be null

Do not use Markdown.
Do not include any text outside the JSON object.
"""


def master_agent_node(
    state: FactoryState,
    db: Session
) -> FactoryState:

    provider = OpenRouterProvider()

    result = provider.generate(
        system_prompt=MASTER_AGENT_PROMPT,
        input_context=state["project_brain"],
        response_model=MasterDecision
    )

    decision = MasterDecision.model_validate_json(
        result["raw_response"]
    )

    return {
        "decision": decision.model_dump(
            mode="json"
        )
    }