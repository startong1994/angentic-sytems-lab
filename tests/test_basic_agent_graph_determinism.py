from __future__ import annotations

from graphs.basic_agent.graph import build_graph
from graphs.basic_agent.state import GraphState


def test_basic_graph_is_deterministic_across_runs() -> None:
    graph = build_graph()

    init = GraphState(trace_id="T-0001", step=0, max_steps=3, history=[])

    histories: list[list[str]] = []
    for _ in range(5):
        # Important: re-create input each run to avoid shared list mutations.
        state_in = init.model_copy(deep=True)
        out = graph.invoke(state_in)

        # LangGraph returns a dict-like state; validate strictly with Pydantic.
        final = GraphState.model_validate(out)
        histories.append(final.history)

    assert all(h == histories[0] for h in histories), histories

    # Expected sequence (3 loops then finish):
    assert histories[0] == ["plan", "verify", "plan", "verify", "plan", "verify", "finish"]
