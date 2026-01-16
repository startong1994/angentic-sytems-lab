from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict


class RunRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    input: str


class RunResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    trace_id: str
    status: Literal["done", "error"]
    result: str | None