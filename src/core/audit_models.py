from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ToolAttemptEvent(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    timestamp_ms: int = Field(..., ge=0)
    event: Literal["tool_attempt"] = "tool_attempt"
    trace_id: str = Field(..., min_length=1)
    tool_name: str = Field(..., min_length=1)

    decision: Literal["allow", "deny"]
    reason: str = Field(..., min_length=1)

    # keep this intentionally constrained: only already-redacted values go here
    params_redacted: dict[str, str] = Field(default_factory=dict)

    # short, grep-friendly
    result_summary: str = Field(..., min_length=1, max_length=240)
