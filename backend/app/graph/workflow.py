from langgraph.graph import StateGraph, START, END
from sqlalchemy.orm import Session

from app.graph.state import FactoryState
from app.services.project_brain import build_project_brain
from app.services.llm_master_agent import decide_with_llm
from app.services.master_decision import validate_master_decision


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
        END
    )

    return graph.compile()