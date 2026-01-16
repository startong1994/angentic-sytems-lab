from __future__ import annotations

import uuid
import logging
from fastapi import FastAPI, Request

# --- NEW IMPORTS ---
from src.app.schemas import RunRequest, RunResponse
from src.graphs.basic_agent.run import run_graph
# Import the logger config from Day 2
from src.middleware.logging import configure_logging 

# 1. Turn on the logs! (This was missing)
configure_logging()

logger = logging.getLogger("app")

app = FastAPI()

# --- THE MIDDLEWARE ---
@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id") or uuid.uuid4().hex
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Trace-Id"] = trace_id
    return response

# --- THE ENDPOINTS ---
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/run", response_model=RunResponse)
def run(req: RunRequest, request: Request) -> RunResponse:
    trace_id = getattr(request.state, "trace_id", "")
    try:
        final = run_graph(input=req.input, trace_id=trace_id)
        return RunResponse(
            trace_id=trace_id, 
            status=final.status, 
            result=final.result
        )
    except Exception:
        logger.exception("run_error", extra={"trace_id": trace_id})
        return RunResponse(
            trace_id=trace_id, 
            status="error", 
            result=None
        )