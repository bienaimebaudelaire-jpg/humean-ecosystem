"""Minimal domain contracts for HUMEAN/RouteCore."""

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


@dataclass(frozen=True)
class Evidence:
    source_url: str
    confidence: float  # 0.0-1.0
    observed_at: str  # ISO 8601 timestamp
    note: str = ""


@dataclass(frozen=True)
class Decision:
    task_id: str
    route: Route
    result_summary: str
    uncertainty: float  # 0.0-1.0, higher = less certain
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    requires_human_approval: bool = False
    audit_ref: str | None = None


@dataclass(frozen=True)
class RegistryDiff:
    capability_id: str
    proposed_change: dict[str, Any]
    confidence: float
    risk_level: str = "medium"  # "low" | "medium" | "high"
    status: str = "pending_human_review"


__all__ = ["Capability", "Decision", "Evidence", "RegistryDiff", "Route", "Task"]
