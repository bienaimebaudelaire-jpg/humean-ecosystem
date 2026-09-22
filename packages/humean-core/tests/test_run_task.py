"""Tests for the run_task end-to-end entry point."""

import sys
import types
import uuid

import pytest

from humean_core import Capability, Task
from humean_core.run_task import _default_executor, run


def _cap(id_, reliability=0.8, source_url="https://example.com"):
    return Capability(
        id=id_,
        kind="model",
        status="active",
        domain="general",
        metadata={"cost_input_usd": 1.0, "cost_output_usd": 0, "reliability": reliability, "source_url": source_url},
    )


def _mock_executor(capability_id: str, prompt: str) -> str:
    return f"mock response from {capability_id}"


def test_normal_task_does_not_require_approval():
    caps = [_cap("cheap-model")]
    task = Task(prompt="hello", domain="general", risk="low")

    decision = run(task, caps, executor=_mock_executor)

    assert decision.route.capability_ids == ("cheap-model",)
    assert decision.requires_human_approval is False
    assert decision.evidence[0].source_url == "https://example.com"


def test_high_risk_task_forces_human_approval():
    caps = [_cap("cheap-model")]
    task = Task(prompt="hello", domain="general", risk="high")

    decision = run(task, caps, executor=_mock_executor)

    assert decision.requires_human_approval is True


def test_execution_failure_produces_decision_not_crash():
    caps = [_cap("cheap-model")]
    task = Task(prompt="hello", domain="general", risk="low")

    def failing_executor(capability_id, prompt):
        raise RuntimeError("boom")

    decision = run(task, caps, executor=failing_executor)

    assert decision.uncertainty == 1.0
    assert decision.requires_human_approval is True
    assert "boom" in decision.result_summary


def test_task_id_is_a_uuid_and_does_not_embed_the_prompt():
    caps = [_cap("cheap-model")]
    task = Task(prompt="this prompt must not leak into the task_id", domain="general", risk="low")

    decision = run(task, caps, executor=_mock_executor)

    assert uuid.UUID(decision.task_id)  # raises ValueError if not a valid UUID
    assert task.prompt not in decision.task_id
    assert decision.route.task_id == decision.task_id


def _stub_capability_probe(monkeypatch, call_fn):
    fake_module = types.ModuleType("capability_probe")
    fake_module.PROVIDERS = {"stub": ("STUB_API_KEY", call_fn)}
    monkeypatch.setitem(sys.modules, "capability_probe", fake_module)


def test_default_executor_returns_provider_response_text(monkeypatch):
    _stub_capability_probe(monkeypatch, lambda prompt: (True, f"response to {prompt}"))

    assert _default_executor("stub", "hello") == "response to hello"


def test_default_executor_raises_on_provider_failure(monkeypatch):
    _stub_capability_probe(monkeypatch, lambda prompt: (False, "boom"))

    with pytest.raises(RuntimeError, match="boom"):
        _default_executor("stub", "hello")


def test_default_executor_raises_not_implemented_when_provider_omits_text(monkeypatch):
    _stub_capability_probe(monkeypatch, lambda prompt: (True, None))

    with pytest.raises(NotImplementedError):
        _default_executor("stub", "hello")
