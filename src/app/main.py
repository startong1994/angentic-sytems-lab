from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

app = FastAPI()


class HealthResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    ok: bool


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(ok=True)
