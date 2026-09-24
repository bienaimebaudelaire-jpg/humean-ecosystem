"""Public GitHub repository watcher for HUMEAN ecosystem projects.

- Uses only GitHub API with GITHUB_TOKEN.
- Produces a Markdown report.
- Optionally opens or updates one stable issue marker to avoid duplicates.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path

from humean_core.repo_watch import (
    DEFAULT_THEMES,
    DEFAULT_TRACKED_REPOSITORIES,
    STABLE_ISSUE_MARKER,
    Theme,
    build_report_markdown,
    deduplicate_candidates,
    filter_candidates,
    parse_search_items,
)

API_BASE = "https://api.github.com"


def _github_request(method: str, url: str, token: str, payload: dict | None = None) -> dict | list:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "token " + token,
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "humean-ecosystem-repo-watch",
    }
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url=url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def _search_repositories(token: str, theme: Theme, *, min_pushed_date: str, per_page: int) -> list[dict]:
    query = f"{theme.query} archived:false is:public pushed:>={min_pushed_date}"
    params = urllib.parse.urlencode({"q": query, "sort": "stars", "order": "desc", "per_page": per_page})
    url = f"{API_BASE}/search/repositories?{params}"
    payload = _github_request("GET", url, token)
    if isinstance(payload, dict):
        return list(payload.get("items") or [])
    return []


def _load_theme_config(path: str | None) -> tuple[Theme, ...]:
    if not path:
        return DEFAULT_THEMES
    content = json.loads(Path(path).read_text(encoding="utf-8"))
    themes: list[Theme] = []
    for entry in content.get("themes", []):
        themes.append(
            Theme(
                name=str(entry["name"]),
                query=str(entry["query"]),
                projects=tuple(str(project) for project in entry.get("projects", [])),
            )
        )
    return tuple(themes) or DEFAULT_THEMES


def _load_tracked_repositories(path: str | None) -> tuple[str, ...]:
    if not path:
        return DEFAULT_TRACKED_REPOSITORIES
    content = json.loads(Path(path).read_text(encoding="utf-8"))
    repos = tuple(str(repo) for repo in content.get("tracked_repositories", []))
    return repos or DEFAULT_TRACKED_REPOSITORIES


def _find_or_create_watch_issue(owner: str, repo: str, token: str, title: str, body: str) -> int:
    issues_url = f"{API_BASE}/repos/{owner}/{repo}/issues?state=open&per_page=100"
    issues = _github_request("GET", issues_url, token)
    if not isinstance(issues, list):
        issues = []

    existing = None
    for issue in issues:
        if "pull_request" in issue:
            continue
        issue_body = str(issue.get("body") or "")
        if STABLE_ISSUE_MARKER in issue_body:
            existing = issue
            break

    if existing:
        issue_number = int(existing["number"])
        patch_url = f"{API_BASE}/repos/{owner}/{repo}/issues/{issue_number}"
        _github_request("PATCH", patch_url, token, payload={"title": title, "body": body})
        return issue_number

    create_url = f"{API_BASE}/repos/{owner}/{repo}/issues"
    created = _github_request("POST", create_url, token, payload={"title": title, "body": body})
    if not isinstance(created, dict) or "number" not in created:
        raise RuntimeError("Unable to create watch issue")
    return int(created["number"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", default=os.getenv("GITHUB_REPOSITORY", "/").split("/")[0])
    parser.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY", "/").split("/")[-1])
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--theme-config", default="")
    parser.add_argument("--tracked-config", default="")
    parser.add_argument("--output", default="/tmp/humean-repo-watch-report.md")
    parser.add_argument("--max-inactive-days", type=int, default=120)
    parser.add_argument("--min-stars", type=int, default=40)
    parser.add_argument("--per-theme", type=int, default=12)
    parser.add_argument("--max-report-rows", type=int, default=25)
    parser.add_argument("--publish-issue", action="store_true")
    args = parser.parse_args()

    token = os.getenv(args.token_env)
    if not token:
        raise RuntimeError(f"Missing required token in env var: {args.token_env}")

    themes = _load_theme_config(args.theme_config or None)
    tracked = _load_tracked_repositories(args.tracked_config or None)

    now = datetime.now(UTC)
    min_pushed_date = (now - timedelta(days=args.max_inactive_days)).date().isoformat()

    all_candidates = []
    for theme in themes:
        items = _search_repositories(token, theme, min_pushed_date=min_pushed_date, per_page=args.per_theme)
        all_candidates.extend(parse_search_items(items, theme))

    filtered = filter_candidates(
        all_candidates,
        min_stars=args.min_stars,
        max_inactive_days=args.max_inactive_days,
        now=now,
    )
    deduped = deduplicate_candidates(filtered)

    report = build_report_markdown(
        deduped,
        tracked_repositories=tracked,
        generated_at=now,
        max_rows=args.max_report_rows,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Report generated: {output_path}")
    print(f"Themes queried: {len(themes)} | candidates={len(all_candidates)} | selected={len(deduped)}")

    if args.publish_issue:
        title = f"[Veille] Dépôts publics IA/orchestration - {now.date().isoformat()}"
        issue_number = _find_or_create_watch_issue(args.owner, args.repo, token, title=title, body=report)
        print(f"Watch issue upserted: #{issue_number}")


if __name__ == "__main__":
    main()
