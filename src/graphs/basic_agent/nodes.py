from __future__ import annotations

from typing import Dict, Any

from .state import GraphState


def plan(state: GraphState) -> Dict[str, Any]:
    # Deterministic mutation: append + increment.
    new_history = [*state.history, "plan"]
    return {"history": new_history, "step": state.step + 1}


def verify(state: GraphState) -> Dict[str, Any]:
    new_history = [*state.history, "verify"]
    return {"history": new_history}


def finish(state: GraphState) -> Dict[str, Any]:
    new_history = [*state.history, "finish"]
    return {"history": new_history}
