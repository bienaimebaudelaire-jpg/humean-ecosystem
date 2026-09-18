"""Minimal domain contracts for HUMEAN/OmniRoute."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Capability:
    id: str
    kind: str
    status: str = "candidate"
    domain: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Task:
    prompt: str
    domain: str | None = None
    risk: str = "low"
    budget_usd: float | None = None


@dataclass(frozen=True)
class Route:
    task_id: str
    capability_ids: tuple[str, ...]
    rationale: str


__all__ = ["Capability", "Route", "Task"]
