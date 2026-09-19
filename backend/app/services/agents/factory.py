from app.models.agent import Agent
from app.services.agents.base import AgentRunner
from app.services.agents.architect import ArchitectAgent


def get_agent_runner(
    agent: Agent
) -> AgentRunner:

    if agent.role == "architect":
        return ArchitectAgent()

    raise ValueError(
        f"No runner implemented for agent role "
        f"'{agent.role}'"
    )