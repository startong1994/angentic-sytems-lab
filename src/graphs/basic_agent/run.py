from __future__ import annotations

from .graph import build_graph
from .state import GraphState


_GRAPH = build_graph()


def run_graph(input: str, trace_id: str) -> GraphState:
    if not trace_id:
        raise ValueError("trace_id is required")

    state_in = GraphState(trace_id=trace_id, input=input, step=0, max_steps=3, history=[])
    out = _GRAPH.invoke(state_in)
    return GraphState.model_validate(out)
