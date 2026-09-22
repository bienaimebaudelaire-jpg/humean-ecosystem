"""Tests for RouteCore's minimal capability selection logic."""

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


def test_unknown_cost_never_beats_a_known_cost():
    no_cost_metadata = Capability(
        id="mystery",
        kind="model",
        status="active",
        domain="general",
        metadata={"reliability": 0.99},  # no cost_input_usd/cost_output_usd at all
    )
    pool = [no_cost_metadata, _cap("paid", cost=2.0)]
    task = Task(prompt="compare plans", domain="general")

    route = select_capability(task, pool, task_id="t4")

    assert route.capability_ids == ("paid",)
    assert "cost_estimate=2.0000" in route.rationale


def test_rationale_flags_unknown_cost_when_selected():
    no_cost_metadata = Capability(
        id="mystery",
        kind="model",
        status="active",
        domain="general",
        metadata={"reliability": 0.99},
    )
    task = Task(prompt="compare plans", domain="general")

    route = select_capability(task, [no_cost_metadata], task_id="t5")

    assert route.capability_ids == ("mystery",)
    assert "unknown" in route.rationale
