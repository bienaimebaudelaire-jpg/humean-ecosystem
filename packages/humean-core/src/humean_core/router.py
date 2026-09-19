"""Minimal routing logic for RouteCore.

Given a Task and a pool of Capability objects, select the best candidate
and return an auditable Route with a human-readable rationale.

Design rules (see docs/ARCHITECTURE.md):
- only "active" capabilities are eligible — "candidate" ones are never
  auto-selected, matching the human-gate principle;
- selection must always produce a rationale string, never a silent pick;
- if no capability qualifies, raise rather than guessing.
"""

from __future__ import annotations

from humean_core import Capability, Route, Task


class NoEligibleCapabilityError(RuntimeError):
    """Raised when no capability in the pool can serve the task."""


def _cost_estimate(capability: Capability) -> float:
    # Foundation-stage heuristic: sum of input/output unit costs if present.
    meta = capability.metadata
    return float(meta.get("cost_input_usd") or 0) + float(meta.get("cost_output_usd") or 0)


def select_capability(task: Task, pool: list[Capability], task_id: str = "unscored") -> Route:
    eligible = [
        c
        for c in pool
        if c.status == "active" and (task.domain is None or c.domain in (None, task.domain))
    ]

    if not eligible:
        raise NoEligibleCapabilityError(
            f"No active capability matches domain={task.domain!r}. "
            "Candidates exist only in 'candidate' status and require human review first."
        )

    # Cheapest eligible capability wins, ties broken by declared reliability.
    eligible.sort(
        key=lambda c: (_cost_estimate(c), -float(c.metadata.get("reliability") or 0))
    )
    chosen = eligible[0]

    rationale = (
        f"Selected '{chosen.id}' (domain={chosen.domain!r}): cheapest active capability "
        f"matching task domain, cost_estimate={_cost_estimate(chosen):.4f}, "
        f"reliability={chosen.metadata.get('reliability', 'unknown')}."
    )

    return Route(task_id=task_id, capability_ids=(chosen.id,), rationale=rationale)
