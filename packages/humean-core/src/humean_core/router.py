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


def _cost_estimate(capability: Capability) -> float | None:
    # Foundation-stage heuristic: sum of input/output unit costs if present.
    # Returns None when neither cost field is declared at all — an unknown
    # cost must never be treated as free, or a capability with no declared
    # price would always win over one with a known, non-zero price.
    meta = capability.metadata
    if "cost_input_usd" not in meta and "cost_output_usd" not in meta:
        return None
    return float(meta.get("cost_input_usd") or 0) + float(meta.get("cost_output_usd") or 0)


def _sort_key(capability: Capability) -> tuple[bool, float, float]:
    cost = _cost_estimate(capability)
    # Unknown-cost capabilities sort after every capability with a known
    # cost (True > False), regardless of how cheap "unknown" might turn
    # out to be.
    return (cost is None, cost or 0.0, -float(capability.metadata.get("reliability") or 0))


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

    # Cheapest eligible capability wins (unknown cost ranks last), ties
    # broken by declared reliability.
    eligible.sort(key=_sort_key)
    chosen = eligible[0]

    cost = _cost_estimate(chosen)
    cost_str = f"{cost:.4f}" if cost is not None else "unknown (no cost declared, ranked last)"

    rationale = (
        f"Selected '{chosen.id}' (domain={chosen.domain!r}): cheapest active capability "
        f"matching task domain, cost_estimate={cost_str}, "
        f"reliability={chosen.metadata.get('reliability', 'unknown')}."
    )

    return Route(task_id=task_id, capability_ids=(chosen.id,), rationale=rationale)
