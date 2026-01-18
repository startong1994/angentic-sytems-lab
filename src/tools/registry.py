from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Type

from pydantic import BaseModel


@dataclass(frozen=True)
class ToolSpec:
    name: str
    request_model: Type[BaseModel]
    response_model: Type[BaseModel]
    handler: Callable[..., BaseModel]
    redact: Callable[[BaseModel], dict[str, str]]


_REGISTRY: dict[str, ToolSpec] = {}


def register_tool(spec: ToolSpec) -> None:
    if spec.name in _REGISTRY:
        raise ValueError(f"tool_already_registered:{spec.name}")
    _REGISTRY[spec.name] = spec


def get_tool(name: str) -> ToolSpec:
    return _REGISTRY[name]


def list_tools() -> list[str]:
    return sorted(_REGISTRY.keys())
