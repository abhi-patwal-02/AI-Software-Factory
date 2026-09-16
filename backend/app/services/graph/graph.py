from langgraph.graph import StateGraph, START, END
from sqlalchemy.orm import Session

from app.services.graph.state import FactoryState
from app.services.graph.nodes.brain import build_brain_node
from app.services.graph.nodes.master import master_agent_node
from app.services.graph.nodes.validator import validate_decision_node


def build_factory_graph(db: Session):

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