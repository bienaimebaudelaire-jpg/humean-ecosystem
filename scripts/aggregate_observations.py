"""Aggregate observed capability_probe results into proposed registry diffs.

Reads data/capability_log.json (written by capability_probe.py --live),
computes observed reliability (success rate) and average latency per
capability, and writes proposals to data/registry_diffs.json.

This never touches capabilities.json or the SQL registry directly —
matches ADR-0002 (proposal-based self-update) and the registry_diffs
table shape in schemas/capability_registry.sql.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def _confidence_for(sample_size: int) -> float:
    # Small samples shouldn't look as trustworthy as large ones.
    if sample_size < 5:
        return 0.3
    if sample_size < 20:
        return 0.6
    return 0.9


def build_diffs(log_records: list[dict]) -> list[dict]:
    by_capability: dict[str, list[dict]] = defaultdict(list)
    for rec in log_records:
        if rec.get("success") is None:
            continue  # scaffold-only entry, not a real observation
        by_capability[rec["capability_id"]].append(rec)

    diffs = []
    for capability_id, records in by_capability.items():
        total = len(records)
        successes = sum(1 for r in records if r["success"])
        latencies = [r["latency_ms"] for r in records if r.get("latency_ms") is not None]

        reliability = round(successes / total, 3)
        avg_latency = round(sum(latencies) / len(latencies)) if latencies else None

        diffs.append(
            {
                "capability_id": capability_id,
                "proposed_change": {
                    "reliability": reliability,
                    "latency_ms": avg_latency,
                    "sample_size": total,
                },
                "confidence": _confidence_for(total),
                "risk_level": "low",  # metadata-only change, no routing/cost/policy impact
                "status": "pending_human_review",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return diffs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="data/capability_log.json")
    parser.add_argument("--out", default="data/registry_diffs.json")
    args = parser.parse_args()

    log_path = Path(args.log)
    if not log_path.exists():
        print(f"No log at {log_path} — run capability_probe.py --live first.")
        return

    records = json.loads(log_path.read_text(encoding="utf-8"))
    diffs = build_diffs(records)

    if not diffs:
        print("No live observations found (all entries were scaffold-only).")
        return

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else []
    existing.extend(diffs)
    out_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")

    for d in diffs:
        print(
            f"[{d['capability_id']}] proposed reliability={d['proposed_change']['reliability']} "
            f"latency_ms={d['proposed_change']['latency_ms']} "
            f"(confidence={d['confidence']}, n={d['proposed_change']['sample_size']}) "
            f"→ status=pending_human_review"
        )


if __name__ == "__main__":
    main()
