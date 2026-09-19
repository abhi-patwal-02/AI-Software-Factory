from app.database import SessionLocal
from app.models.agent import Agent
from app.models.task import Task
from app.services.agent_execution import execute_agent_task


db = SessionLocal()

try:

    task = db.get(
        Task,
        12
    )

    agent = db.get(
        Agent,
        2
    )

    if not task:
        raise ValueError("Task 12 not found")

    if not agent:
        raise ValueError("Agent 2 not found")

    result = execute_agent_task(
        task,
        agent,
        db
    )

    print("\n===== AGENT EXECUTION =====")
    print(result)

finally:
    db.close()