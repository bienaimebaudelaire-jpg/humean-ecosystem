"""Probe configured providers without writing secrets to source control.

Default behavior (unchanged): just check which API keys are configured,
write a scaffold record, and do nothing else — no network calls.

With --live: actually call each configured provider once, measure real
latency and success, and log it. Still never writes to capabilities.json
or the SQL registry directly — see aggregate_observations.py for that,
which only ever produces a *proposed* diff (ADR-0002).
"""

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


def _call_claude(prompt: str) -> tuple[bool, str | None]:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=50,
        messages=[{"role": "user", "content": prompt}],
    )
    return True, response.content[0].text


def _call_gemini(prompt: str) -> tuple[bool, str | None]:
    import google.generativeai as genai

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return True, response.text


def _call_deepseek(prompt: str) -> tuple[bool, str | None]:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat", messages=[{"role": "user", "content": prompt}]
    )
    return True, response.choices[0].message.content


# capability_id must match the ids used in the capability registry (schemas/,
# capabilities.example.json) so that observed data can be joined back to it.
PROVIDERS: dict[str, tuple[str, object]] = {
    "claude-sonnet-4-6": ("ANTHROPIC_API_KEY", _call_claude),
    "gemini": ("GEMINI_API_KEY", _call_gemini),
    "deepseek-chat": ("DEEPSEEK_API_KEY", _call_deepseek),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="Explain subscription comparison in two sentences.")
    parser.add_argument("--log", default=os.getenv("HUMEAN_CAPABILITY_LOG", "data/capability_log.json"))
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually call configured providers (costs money/tokens). Off by default.",
    )
    args = parser.parse_args()

    if not args.live:
        print("Capability probe scaffold: provider calls are intentionally opt-in. Use --live to call them.")

    for capability_id, (key_name, call_fn) in PROVIDERS.items():
        configured = bool(os.getenv(key_name))
        entry: dict[str, object] = {
            "capability_id": capability_id,
            "configured": configured,
            "success": None,
            "latency_ms": None,
            "prompt_fingerprint": str(hash(args.prompt)),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Provider invocation not enabled in foundation scaffold.",
        }

        if args.live and configured:
            start = time.perf_counter()
            try:
                success, text_or_error = call_fn(args.prompt)
            except Exception as exc:  # noqa: BLE001 — probe must never crash the batch
                success, text_or_error = False, str(exc)
            entry["latency_ms"] = round((time.perf_counter() - start) * 1000)
            entry["success"] = success
            entry["note"] = "Live call succeeded." if success else (text_or_error or "Live call failed.")
            entry["response_text"] = text_or_error if success else None

        record(Path(args.log), entry)
        status = "skipped (no key)" if not configured else ("live" if args.live else "scaffold-only")
        print(f"[{capability_id}] configured={configured} mode={status} success={entry['success']}")


if __name__ == "__main__":
    main()
