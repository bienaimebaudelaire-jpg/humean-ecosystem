"""Tests for the minimal OmniRoute selection logic."""

import pytest

from humean_core import Capability, Task
from humean_core.router import NoEligibleCapabilityError, select_capability


def _cap(id_, status="active", domain="general", cost=1.0, reliability=0.9):
    return Capability(
        id=id_,
        kind="model",
        status=status,
        domain=domain,
        metadata={"cost_input_usd": cost, "cost_output_usd": 0, "reliability": reliability},
    )


def test_picks_cheapest_active_capability():
    pool = [_cap("expensive", cost=10.0), _cap("cheap", cost=1.0)]
    task = Task(prompt="compare plans", domain="general")

    route = select_capability(task, pool, task_id="t1")

    assert route.capability_ids == ("cheap",)
    assert "cheap" in route.rationale


def test_never_selects_candidate_status():
    pool = [_cap("unproven", status="candidate", cost=0.01)]
    task = Task(prompt="compare plans", domain="general")

    with pytest.raises(NoEligibleCapabilityError):
        select_capability(task, pool, task_id="t2")


def test_domain_filtering():
    pool = [_cap("finance-model", domain="finance", cost=1.0)]
    task = Task(prompt="general question", domain="general")

    with pytest.raises(NoEligibleCapabilityError):
        select_capability(task, pool, task_id="t3")
