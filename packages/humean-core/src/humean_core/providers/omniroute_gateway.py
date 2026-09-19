"""Client for a self-hosted OmniRoute gateway (github.com/diegosouzapw/OmniRoute).

RouteCore's executor calls this when a Capability's metadata declares a
`gateway_model` (see make_gateway_executor). The gateway exposes an
OpenAI-compatible POST /v1/chat/completions and echoes routing/cost
telemetry as X-OmniRoute-* response headers -- see
docs/reference/API_REFERENCE.md in diegosouzapw/OmniRoute.

Kept dependency-free (stdlib urllib only) to match humean-core's "generic
infrastructure first" principle -- see pyproject.toml's [providers] comment.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from humean_core import Capability

# (url, body, headers) -> (status_code, response_body, response_headers)
Transport = Callable[[str, bytes, dict], tuple]

DEFAULT_BASE_URL = "http://localhost:20128/v1"  # gateway's documented self-host default


class OmniRouteGatewayError(RuntimeError):
    """Raised when the self-hosted gateway rejects or fails a request."""


@dataclass(frozen=True)
class GatewayResponse:
    text: str
    provider: str | None
    cost_usd: float | None
    cache_hit: bool
    latency_ms: float | None
    decision_trace: str | None
    request_id: str | None


def _default_transport(url: str, body: bytes, headers: dict) -> tuple:
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 - self-hosted, trusted gateway
            return resp.status, resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), dict(exc.headers or {})


def _header(headers: dict, name: str) -> str | None:
    for k, v in headers.items():
        if k.lower() == name.lower():
            return v
    return None


def call_gateway(
    model: str,
    prompt: str,
    *,
    base_url: str | None = None,
    api_key: str | None = None,
    transport: Transport = _default_transport,
) -> GatewayResponse:
    """Call a self-hosted OmniRoute gateway's OpenAI-compatible chat endpoint.

    base_url defaults to $ROUTECORE_OMNIROUTE_BASE_URL or DEFAULT_BASE_URL.
    api_key defaults to $ROUTECORE_OMNIROUTE_API_KEY.
    """
    base_url = (base_url or os.environ.get("ROUTECORE_OMNIROUTE_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    api_key = api_key or os.environ.get("ROUTECORE_OMNIROUTE_API_KEY")
    if not api_key:
        raise OmniRouteGatewayError(
            "No API key: set ROUTECORE_OMNIROUTE_API_KEY or pass api_key explicitly."
        )

    payload = json.dumps(
        {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}
    ).encode("utf-8")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    status, body, resp_headers = transport(f"{base_url}/chat/completions", payload, headers)
    if status >= 400:
        raise OmniRouteGatewayError(f"Gateway returned HTTP {status}: {body[:500]!r}")

    data = json.loads(body)
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise OmniRouteGatewayError(f"Unexpected gateway response shape: {data!r}") from exc

    cost_raw = _header(resp_headers, "X-OmniRoute-Response-Cost")
    latency_raw = _header(resp_headers, "X-OmniRoute-Latency-Ms")

    return GatewayResponse(
        text=text,
        provider=_header(resp_headers, "X-OmniRoute-Provider"),
        cost_usd=float(cost_raw) if cost_raw is not None else None,
        cache_hit=(_header(resp_headers, "X-OmniRoute-Cache-Hit") or "").lower() == "true",
        latency_ms=float(latency_raw) if latency_raw is not None else None,
        decision_trace=_header(resp_headers, "X-OmniRoute-Decision"),
        request_id=_header(resp_headers, "X-OmniRoute-Request-Id"),
    )


def make_gateway_executor(capabilities: "list[Capability]"):
    """Build a run_task.Executor that routes through the self-hosted gateway.

    Looks up each capability's `metadata["gateway_model"]` (the gateway's
    own model id, e.g. "cc/claude-sonnet-4-6") and calls it via call_gateway.
    """
    by_id = {c.id: c for c in capabilities}

    def _executor(capability_id: str, prompt: str) -> str:
        cap = by_id.get(capability_id)
        if cap is None or "gateway_model" not in cap.metadata:
            raise OmniRouteGatewayError(
                f"'{capability_id}' has no gateway_model in its metadata -- not a gateway-routed capability."
            )
        return call_gateway(cap.metadata["gateway_model"], prompt).text

    return _executor


__all__ = [
    "DEFAULT_BASE_URL",
    "GatewayResponse",
    "OmniRouteGatewayError",
    "call_gateway",
    "make_gateway_executor",
]
