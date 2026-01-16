from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class GraphState(BaseModel):
    """
    Minimal deterministic state for a bounded LangGraph loop.
    Keep it pure: no timestamps, no random IDs generated inside nodes.
    """
    model_config = ConfigDict(strict=True)

    trace_id: str = Field(min_length=1)
    input: str = ""  # added
    step: int = 0
    max_steps: int = 3
    history: list[str] = Field(default_factory=list)

    status: Literal["done", "error"] = "done"  # added
    result: str | None = None  # added

