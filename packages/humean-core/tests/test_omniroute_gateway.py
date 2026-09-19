"""Tests for the OmniRoute gateway client -- no real network involved.

A fake transport is injected everywhere (same pattern as test_run_task.py's
injectable executor), so these exercise header parsing and error handling
without needing a running self-hosted gateway.
"""

from __future__ import annotations

import json

import pytest
from humean_core import Capability
from humean_core.providers.omniroute_gateway import (
    OmniRouteGatewayError,
    call_gateway,
    make_gateway_executor,
)


def _fake_transport(status: int, body: dict, headers: dict):
    def _transport(url: str, payload: bytes, req_headers: dict):
        assert req_headers["Authorization"] == "Bearer test-key"
        assert json.loads(payload)["model"] == "cc/claude-sonnet-4-6"
        return status, json.dumps(body).encode("utf-8"), headers
    return _transport


def test_call_gateway_parses_response_and_cost_headers():
    transport = _fake_transport(
        200,
        {"choices": [{"message": {"content": "hello"}}]},
        {
            "X-OmniRoute-Provider": "anthropic",
            "X-OmniRoute-Response-Cost": "0.0012000000",
            "X-OmniRoute-Cache-Hit": "false",
            "X-OmniRoute-Latency-Ms": "842",
            "X-OmniRoute-Decision": "strategy=cheapest; provider=anthropic; latency_ms=842",
            "X-OmniRoute-Request-Id": "req_123",
        },
    )
    result = call_gateway(
        "cc/claude-sonnet-4-6", "hi", api_key="test-key", transport=transport
    )
    assert result.text == "hello"
    assert result.provider == "anthropic"
    assert result.cost_usd == pytest.approx(0.0012)
    assert result.cache_hit is False
    assert result.latency_ms == pytest.approx(842)
    assert "cheapest" in result.decision_trace
    assert result.request_id == "req_123"


def test_call_gateway_cache_hit_is_case_insensitive_header_match():
    transport = _fake_transport(
        200,
        {"choices": [{"message": {"content": "cached"}}]},
        {"x-omniroute-cache-hit": "true"},
    )
    result = call_gateway("cc/claude-sonnet-4-6", "hi", api_key="test-key", transport=transport)
    assert result.cache_hit is True


def test_call_gateway_requires_api_key(monkeypatch):
    monkeypatch.delenv("ROUTECORE_OMNIROUTE_API_KEY", raising=False)
    with pytest.raises(OmniRouteGatewayError, match="No API key"):
        call_gateway("cc/claude-sonnet-4-6", "hi", transport=_fake_transport(200, {}, {}))


def test_call_gateway_raises_on_http_error():
    transport = _fake_transport(429, {"error": "rate limited"}, {})
    with pytest.raises(OmniRouteGatewayError, match="HTTP 429"):
        call_gateway("cc/claude-sonnet-4-6", "hi", api_key="test-key", transport=transport)


def test_call_gateway_raises_on_malformed_body():
    transport = _fake_transport(200, {"unexpected": "shape"}, {})
    with pytest.raises(OmniRouteGatewayError, match="Unexpected gateway response shape"):
        call_gateway("cc/claude-sonnet-4-6", "hi", api_key="test-key", transport=transport)


def test_make_gateway_executor_looks_up_gateway_model():
    cap = Capability(
        id="gateway/claude-sonnet-4-6",
        kind="model",
        status="candidate",
        domain="general",
        metadata={"gateway_model": "cc/claude-sonnet-4-6"},
    )
    transport = _fake_transport(200, {"choices": [{"message": {"content": "ok"}}]}, {})
    executor = make_gateway_executor([cap])
    # monkeypatch call_gateway's transport indirectly via env + injected transport
    import humean_core.providers.omniroute_gateway as gw

    orig = gw.call_gateway

    def _patched(model, prompt, **kwargs):
        return orig(model, prompt, api_key="test-key", transport=transport)

    gw.call_gateway = _patched
    try:
        assert executor("gateway/claude-sonnet-4-6", "hi") == "ok"
    finally:
        gw.call_gateway = orig


def test_make_gateway_executor_rejects_non_gateway_capability():
    cap = Capability(id="claude-sonnet-4-6", kind="model", status="active", domain="general")
    executor = make_gateway_executor([cap])
    with pytest.raises(OmniRouteGatewayError, match="no gateway_model"):
        executor("claude-sonnet-4-6", "hi")
