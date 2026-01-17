from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ReadFileRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    path: str = Field(..., min_length=1, description="Relative path under ./data/ e.g. data/sample.txt")


class ReadFileResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    ok: bool
    bytes: int | None = None
    preview: str | None = None
    error: str | None = None
