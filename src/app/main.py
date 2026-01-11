from fastapi import FastAPI
from fastapi import Request
from pydantic import BaseModel, ConfigDict
from src.middleware.trace_id import TraceIdMiddleware
from src.middleware.logging import configure_logging, RequestLoggingMiddleware
from src.middleware.spans import Span

configure_logging()

app = FastAPI()


app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(TraceIdMiddleware)





class HealthResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    ok: bool


@app.get("/healthz")
async def healthz(request: Request):
    with Span("healthz", request.state.trace_id):
        return {"ok": True}

