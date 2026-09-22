"""Single entry point: task in, Decision out.

Chains together what already exists:
  registry.load_capabilities()  → pool of known capabilities
  router.select_capability()    → which one handles this task
  executor (pluggable)          → actually calls the provider
  → wraps everything into a Decision with Evidence, auditable end to end

The executor is injectable so this can be tested without real API calls
(see test_run_task.py) and so scripts/capability_probe.py's provider
functions can be reused as the default executor.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable
from uuid import uuid4

from humean_core import Capability, Decision, Evidence, Task
from humean_core.router import NoEligibleCapabilityError, select_capability

Executor = Callable[[str, str], str]  # (capability_id, prompt) -> response text


def _default_executor(capability_id: str, prompt: str) -> str:
    """Falls back to scripts/capability_probe.py's provider calls.

    Imported lazily so humean-core doesn't hard-depend on provider SDKs
    (see pyproject.toml's [providers] optional group).

    This only works from a source checkout of this monorepo, where
    scripts/ sits four directories above this file. Once humean-core is
    installed as a standalone package, scripts/ won't exist on disk next
    to it — pass a custom `executor=...` to run() instead (e.g. one built
    from humean_core.providers.omniroute_gateway.make_gateway_executor).
    """
    import sys
    from pathlib import Path

    scripts_dir = Path(__file__).resolve().parents[4] / "scripts"
    if not scripts_dir.is_dir():
        raise ImportError(
            "The default executor requires a source checkout of the "
            f"humean-ecosystem monorepo (expected scripts/ at {scripts_dir}); "
            "pass a custom executor=... to run() instead."
        )
    sys.path.insert(0, str(scripts_dir))
    from capability_probe import PROVIDERS  # type: ignore

    if capability_id not in PROVIDERS:
        raise ValueError(f"No executor available for '{capability_id}'.")
    _, call_fn = PROVIDERS[capability_id]
    success, text = call_fn(prompt)
    if not success:
        raise RuntimeError(text or "provider call failed")
    if text is None:
        raise NotImplementedError(
            f"Provider for '{capability_id}' does not return response text yet."
        )
    return text


def run(
    task: Task,
    capabilities: list[Capability],
    executor: Executor = _default_executor,
) -> Decision:
    """Run a task end to end and return an auditable Decision.

    Never swallows routing failures — if no capability qualifies, this
    raises NoEligibleCapabilityError rather than silently degrading.
    """
    task_id = str(uuid4())
    route = select_capability(task, capabilities, task_id=task_id)
    capability_id = route.capability_ids[0]
    capability = next(c for c in capabilities if c.id == capability_id)

    started_at = datetime.now(timezone.utc).isoformat()
    try:
        result_text = executor(capability_id, task.prompt)
        failed = False
    except Exception as exc:  # noqa: BLE001 — must always produce a Decision, even on failure
        result_text = f"Execution failed: {exc}"
        failed = True

    reliability = capability.metadata.get("reliability")
    # Foundation-stage heuristic: uncertainty rises when reliability is
    # unknown or low, and always maxes out on execution failure.
    uncertainty = 1.0 if failed else round(1.0 - float(reliability or 0.5), 3)

    evidence = (
        Evidence(
            source_url=capability.metadata.get("source_url", ""),
            confidence=float(reliability or 0.5),
            observed_at=started_at,
            note=route.rationale,
        ),
    )

    return Decision(
        task_id=task_id,
        route=route,
        result_summary=result_text,
        uncertainty=uncertainty,
        evidence=evidence,
        requires_human_approval=(task.risk == "high") or failed,
        audit_ref=None,
    )
