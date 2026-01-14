from __future__ import annotations

from typing import Any, Literal

from langgraph.graph import END, StateGraph

from .nodes import plan, verify, finish
from .state import GraphState


def _make_state_graph() -> StateGraph:
    """
    LangGraph has had small API variations across versions.
    This keeps your code resilient without changing behavior.
    """
    try:
        return StateGraph(GraphState)  # common form
    except TypeError:
        return StateGraph(state_schema=GraphState)  # some versions


def _route_after_verify(state: GraphState) -> Literal["plan", "finish"]:
    # stop when step >= max_steps (step increments in plan)
    return "finish" if state.step >= state.max_steps else "plan"


def build_graph() -> Any:
    g = _make_state_graph()

    g.add_node("plan", plan)
    g.add_node("verify", verify)
    g.add_node("finish", finish)

    g.set_entry_point("plan")
    g.add_edge("plan", "verify")
    g.add_conditional_edges(
        "verify",
        _route_after_verify,
        {"plan": "plan", "finish": "finish"},
    )
    g.add_edge("finish", END)

    return g.compile()
