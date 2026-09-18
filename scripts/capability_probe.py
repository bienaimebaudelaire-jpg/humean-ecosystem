"""Probe configured providers without writing secrets to source control."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path


def record(log_path: Path, entry: dict[str, object]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    records = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
    records.append(entry)
    log_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="Explain subscription comparison in two sentences.")
    parser.add_argument("--log", default=os.getenv("HUMEAN_CAPABILITY_LOG", "data/capability_log.json"))
    args = parser.parse_args()
    print("Capability probe scaffold: provider calls are intentionally opt-in.")
    for capability_id, key_name in (("claude", "ANTHROPIC_API_KEY"), ("gemini", "GEMINI_API_KEY"), ("deepseek", "DEEPSEEK_API_KEY")):
        start = time.perf_counter()
        configured = bool(os.getenv(key_name))
        record(Path(args.log), {
            "capability_id": capability_id,
            "configured": configured,
            "success": None,
            "latency_ms": round((time.perf_counter() - start) * 1000),
            "prompt_fingerprint": str(hash(args.prompt)),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Provider invocation not enabled in foundation scaffold.",
        })
        print(f"[{capability_id}] configured={configured}")


if __name__ == "__main__":
    main()
