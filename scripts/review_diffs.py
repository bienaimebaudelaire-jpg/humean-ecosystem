"""Human Gate: interactively review pending registry diffs.

Reads data/registry_diffs.json (written by aggregate_observations.py),
shows each "pending_human_review" entry, and asks for an explicit
approve/reject decision. Approved diffs are merged into capabilities.json.
Nothing is ever applied automatically — see ADR-0002.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def _save(path: Path, data: list[dict]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def apply_diff(capabilities: list[dict], diff: dict) -> bool:
    for cap in capabilities:
        if cap["id"] == diff["capability_id"]:
            cap.update(diff["proposed_change"])
            cap["updated_at"] = datetime.now(timezone.utc).isoformat()
            return True
    return False  # capability_id not found — do not silently create one


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diffs", default="data/registry_diffs.json")
    parser.add_argument("--capabilities", default="schemas/capabilities.json")
    parser.add_argument(
        "--yes-to-all",
        action="store_true",
        help="Skip interactive prompts and approve every pending diff (use with care).",
    )
    args = parser.parse_args()

    diffs_path = Path(args.diffs)
    caps_path = Path(args.capabilities)

    diffs = _load(diffs_path)
    capabilities = _load(caps_path)

    pending = [d for d in diffs if d.get("status") == "pending_human_review"]
    if not pending:
        print("No pending diffs to review.")
        return

    for diff in pending:
        change = diff["proposed_change"]
        print(f"\n--- {diff['capability_id']} ---")
        print(f"  proposed: {change}")
        print(f"  confidence={diff['confidence']}  risk_level={diff.get('risk_level', 'unknown')}")

        if args.yes_to_all:
            decision = "y"
        else:
            decision = input("  Approve? [y/N] ").strip().lower()

        if decision == "y":
            applied = apply_diff(capabilities, diff)
            diff["status"] = "approved" if applied else "rejected"
            if not applied:
                print(f"  ⚠️  capability_id '{diff['capability_id']}' not found in {caps_path} — rejected.")
            else:
                print("  ✅ applied.")
        else:
            diff["status"] = "rejected"
            print("  ❌ rejected.")

        diff["reviewed_at"] = datetime.now(timezone.utc).isoformat()

    _save(diffs_path, diffs)
    _save(caps_path, capabilities)
    print(f"\nUpdated {caps_path} and {diffs_path}.")


if __name__ == "__main__":
    main()
