"""Local capability registry loader.

Reads capabilities from a JSON file shaped like the `capabilities` table
in schemas/capability_registry.sql. This is a foundation-stage reader —
no database connection yet, just enough to let the router work against
real (if manually curated) data.
"""

from __future__ import annotations

import json
from pathlib import Path

from humean_core import Capability


def load_capabilities(path: str | Path) -> list[Capability]:
    """Load capabilities from a JSON file.

    Expected shape per entry (extra fields are kept in `metadata`):
        {
          "id": "claude-sonnet-4-6",
          "kind": "model",
          "status": "active",
          "domain": "general",
          "cost_input_usd": 3.0,
          "cost_output_usd": 15.0,
          "latency_ms": 1200,
          "reliability": 0.98
        }
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    capabilities: list[Capability] = []
    known_fields = {"id", "kind", "status", "domain"}
    for entry in data:
        metadata = {k: v for k, v in entry.items() if k not in known_fields}
        capabilities.append(
            Capability(
                id=entry["id"],
                kind=entry["kind"],
                status=entry.get("status", "candidate"),
                domain=entry.get("domain"),
                metadata=metadata,
            )
        )
    return capabilities
