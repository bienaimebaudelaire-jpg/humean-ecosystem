"""Smoke tests for the initial HUMEAN contracts."""

from humean_core import Capability, Task


def test_contracts_are_explicit():
    task = Task(prompt="compare plans", domain="subscriptions")
    capability = Capability(id="example", kind="llm", status="candidate")
    assert task.domain == "subscriptions"
    assert capability.kind == "llm"
