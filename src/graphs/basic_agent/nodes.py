from __future__ import annotations

import time
from typing import Any, Callable, Dict

from .state import GraphState

# Import your Day 2 JSON logger (adjust import to your repo)
# from src.app.logging import get_logger
import logging
logger = logging.getLogger("app")



def _node_span(node_name: str) -> Callable[[Callable[[GraphState], Dict[str, Any]]], Callable[[GraphState], Dict[str, Any]]]:
    def deco(fn: Callable[[GraphState], Dict[str, Any]]) -> Callable[[GraphState], Dict[str, Any]]:
        def wrapped(state: GraphState) -> Dict[str, Any]:
            t0 = time.perf_counter()
            logger.info(
                "node_start",
                extra={"trace_id": state.trace_id, "node": node_name, "status": "start"},
            )
            try:
                patch = fn(state)
                dt_ms = int((time.perf_counter() - t0) * 1000)
                logger.info(
                    "node_end",
                    extra={"trace_id": state.trace_id, "node": node_name, "status": "ok", "duration_ms": dt_ms},
                )
                return patch
            except Exception:
                dt_ms = int((time.perf_counter() - t0) * 1000)
                logger.exception(
                    "node_end",
                    extra={"trace_id": state.trace_id, "node": node_name, "status": "error", "duration_ms": dt_ms},
                )
                raise
        return wrapped
    return deco


@_node_span("plan")
def plan(state: GraphState) -> Dict[str, Any]:
    # Failure path requirement:
    if state.input == "fail":
        raise RuntimeError("forced failure for Day 4 proof")

    new_history = [*state.history, "plan"]
    return {"history": new_history, "step": state.step + 1}


@_node_span("verify")
def verify(state: GraphState) -> Dict[str, Any]:
    new_history = [*state.history, "verify"]
    return {"history": new_history}


@_node_span("finish")
def finish(state: GraphState) -> Dict[str, Any]:
    new_history = [*state.history, "finish"]
    # deterministic result
    return {"history": new_history, "status": "done", "result": f"ok:{state.input}"}
