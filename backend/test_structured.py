import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


response = llm.invoke(
    """
You are a decision engine.

Return ONLY this JSON object.
Do not use Markdown.
Do not explain anything.

{
  "action": "assign_task",
  "task_id": 12,
  "agent_id": 2,
  "reason": "Task 12 requires an architect and agent 2 is idle."
}

Return exactly one JSON object with these four fields:
action, task_id, agent_id, reason.
"""
)


print("RAW RESPONSE:")
print(repr(response.content))