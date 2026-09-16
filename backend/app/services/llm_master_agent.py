import time

from sqlalchemy.orm import Session

from app.models.llm_interaction import LLMInteraction
from app.schemas.master_decision import MasterDecision
from app.services.llm.openrouter_provider import OpenRouterProvider
from app.services.master_decision import validate_master_decision
from app.services.project_brain import build_project_brain


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
- Return only a MasterDecision.

Output requirements:

- Always include the "action" field.
- Always include the "reason" field.
- "reason" must be a concise explanation of the decision.
- For "assign_task", always include "task_id" and "agent_id".
- For "handle_error", always include "error_id" and "agent_id".
- For "wait", task_id, error_id, and agent_id must be null.
- Return a single JSON object.
- Do not wrap the JSON in Markdown code fences.
- Do not include any text before or after the JSON.
"""


def decide_with_llm(
    project_id: int,
    db: Session
) -> MasterDecision:

    brain = build_project_brain(
        project_id,
        db
    )

    brain_context = brain.model_dump(
        mode="json"
    )

    provider = OpenRouterProvider()

    start_time = time.perf_counter()

    try:

        result = provider.generate(
            system_prompt=MASTER_AGENT_PROMPT,
            input_context=brain_context,
            response_model=MasterDecision
        )

        latency_ms = int(
            (time.perf_counter() - start_time) * 1000
        )
        
        # print("\nRAW LLM RESPONSE:")
        # print(result["raw_response"])
        # print()

        decision = MasterDecision.model_validate_json(
            result["raw_response"]
        )

        validate_master_decision(
            decision,
            db
        )

        interaction = LLMInteraction(
            project_id=project_id,
            agent_id=1,
            provider="openrouter",
            model=result["model"],
            system_prompt=MASTER_AGENT_PROMPT,
            input_context=brain_context,
            raw_response=result["raw_response"],
            parsed_decision=decision.model_dump(
                mode="json"
            ),
            status="success",
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            latency_ms=latency_ms
        )

        db.add(interaction)
        db.commit()

        return decision

    except Exception as exc:

        latency_ms = int(
            (time.perf_counter() - start_time) * 1000
        )

        interaction = LLMInteraction(
            project_id=project_id,
            agent_id=1,
            provider="openrouter",
            model=provider.model,
            system_prompt=MASTER_AGENT_PROMPT,
            input_context=brain_context,
            raw_response=result.get("raw_response") if "result" in locals() else None,
            status="failed",
            error_message=str(exc),
            input_tokens=result.get("input_tokens") if "result" in locals() else None,
            output_tokens=result.get("output_tokens") if "result" in locals() else None,
            latency_ms=latency_ms
        )

        db.add(interaction)
        db.commit()

        raise