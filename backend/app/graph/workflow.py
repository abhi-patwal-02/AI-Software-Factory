from langgraph.graph import StateGraph, START, END
from sqlalchemy.orm import Session

from app.graph.state import FactoryState
from app.services.project_brain import build_project_brain
from app.services.llm_master_agent import decide_with_llm
from app.services.master_decision import validate_master_decision
from app.services.decision_executor import execute_decision
from app.models.agent import Agent
from app.models.task import Task
from app.services.agent_execution import execute_agent_task


def build_brain_node(
    state: FactoryState,
    db: Session
) -> dict:

    brain = build_project_brain(
        state["project_id"],
        db
    )

    return {
        "project_brain": brain.model_dump(
            mode="json"
        )
    }


def master_agent_node(
    state: FactoryState,
    db: Session
) -> dict:

    decision = decide_with_llm(
        state["project_id"],
        db
    )

    return {
        "decision": decision
    }


def validate_decision_node(
    state: FactoryState,
    db: Session
) -> dict:

    decision = state["decision"]

    validate_master_decision(
        decision,
        db
    )

    return {
        "error": None
    }

def execute_decision_node(
    state: FactoryState,
    db: Session
) -> dict:

    decision = state["decision"]

    execute_decision(
        decision,
        db
    )

    return {
        "error": None
    }
    
def execute_agent_node(
    state: FactoryState,
    db: Session
) -> dict:

    decision = state["decision"]

    if decision.action != "assign_task":
        return {
            "error": None
        }

    task = db.get(
        Task,
        decision.task_id
    )

    agent = db.get(
        Agent,
        decision.agent_id
    )

    if not task:
        raise ValueError(
            "Task not found during agent execution"
        )

    if not agent:
        raise ValueError(
            "Agent not found during agent execution"
        )

    result = execute_agent_task(
        task,
        agent,
        db
    )

    print("\n===== AGENT RESULT =====")
    print(result)

    return {
        "error": None
    }


def build_factory_graph(
    db: Session
):

    graph = StateGraph(FactoryState)

    graph.add_node(
        "build_brain",
        lambda state: build_brain_node(
            state,
            db
        )
    )

    graph.add_node(
        "master_agent",
        lambda state: master_agent_node(
            state,
            db
        )
    )

    graph.add_node(
        "validate_decision",
        lambda state: validate_decision_node(
            state,
            db
        )
    )
    
    graph.add_node(
        "execute_decision",
        lambda state: execute_decision_node(
            state,
            db
        )
    )
    
    graph.add_node(
    "execute_agent",
    lambda state: execute_agent_node(
        state,
        db
    )
)

    graph.add_edge(
        START,
        "build_brain"
    )

    graph.add_edge(
        "build_brain",
        "master_agent"
    )

    graph.add_edge(
        "master_agent",
        "validate_decision"
    )

    graph.add_edge(
        "validate_decision",
        "execute_decision"
    )

    graph.add_edge(
        "execute_decision",
        "execute_agent"
    )

    graph.add_edge(
        "execute_agent",
        END
    )

    return graph.compile()