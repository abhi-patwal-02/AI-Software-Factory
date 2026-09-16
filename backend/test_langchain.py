from app.services.llm.openrouter_provider import OpenRouterProvider
from app.schemas.master_decision import MasterDecision


provider = OpenRouterProvider()

print("Provider initialized")
print("Model:", provider.model)


result = provider.generate(
    system_prompt="""
You are a test Master Agent.

Return ONLY one JSON object.

Assign task 12 to agent 2.

The task:
- task_id: 12
- title: Design system architecture
- required_role: architect

The agent:
- agent_id: 2
- role: architect
- status: idle

The JSON must contain exactly these fields:

action
task_id
error_id
agent_id
reason

For this decision:
- action must be "assign_task"
- task_id must be 12
- error_id must be null
- agent_id must be 2
- reason must explain the assignment.

Do not use Markdown.
Do not include any text outside the JSON object.
""",

    input_context={
        "task_id": 12,
        "agent_id": 2
    },

    response_model=MasterDecision
)


print("\nRaw response:")
print(result["raw_response"])


decision = MasterDecision.model_validate_json(
    result["raw_response"]
)


print("\nParsed decision:")
print(decision.model_dump_json(indent=2))