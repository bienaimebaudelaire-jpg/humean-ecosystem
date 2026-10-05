"""Smoke tests for the initial HUMEAN contracts."""

import json
from pathlib import Path

from humean_core import Capability, Task


def test_contracts_are_explicit():
    task = Task(prompt="compare plans", domain="subscriptions")
    capability = Capability(id="example", kind="llm", status="candidate")
    assert task.domain == "subscriptions"
    assert capability.kind == "llm"


def test_openshell_runtime_example_is_a_candidate_with_placeholder_access():
    capabilities = json.loads(
        (Path(__file__).parents[3] / "schemas" / "capabilities.example.json").read_text()
    )
    runtime_capability = next(
        capability
        for capability in capabilities
        if capability["id"] == "openshell-agent-runtime"
    )
    runtime = runtime_capability["metadata"]["runtime"]

    assert runtime_capability["kind"] == "agent"
    assert runtime_capability["status"] == "candidate"
    assert runtime["backend"] == "openshell"
    assert runtime["approved_endpoints"] == ["https://inference.example.invalid"]
    assert runtime["credential_ref"] == "secret://deployment/REPLACE_ME"
