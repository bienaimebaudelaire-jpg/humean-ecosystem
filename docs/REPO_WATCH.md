# Public repository watcher

The repository watcher runs periodic public-GitHub discovery for topics relevant to HUMEAN projects.

## Goals

- discover active/public repositories in selected themes;
- compare them with tracked repositories;
- produce a traceable Markdown report;
- open or update a single watch issue using a stable marker to avoid duplicates.

## Schedule

Workflow: `.github/workflows/repo-watch.yml`

- `cron: 0 8 1,16 * *` (1st and 16th at 08:00 UTC)
- manual trigger via `workflow_dispatch`

This approximates a 15-day cadence (GitHub cron cannot express "every 15 days" exactly).

## Authentication

Only `GITHUB_TOKEN` is used. No extra API key is required.

## Configurable scope

Defaults are in `humean_core.repo_watch`:

- themes:
  - AI agents/autonomous agents
  - orchestration/governance
  - TypeScript/Python LLM tooling
  - fact checking/provenance
  - travel planning
  - video automation
- tracked repositories include:
  - `Conway-Research/automaton`
  - `bienaimebaudelaire-jpg/humean-ecosystem`
  - `bienaimebaudelaire-jpg/humean-ai`
  - `bienaimebaudelaire-jpg/fact-check-app`
  - `bienaimebaudelaire-jpg/time-travel-companion`
  - `bienaimebaudelaire-jpg/laboiteaboulon`
  - `bienaimebaudelaire-jpg/Agent-Reach`

Optional JSON overrides:

- `--theme-config path/to/file.json` with `{ "themes": [{"name": "...", "query": "...", "projects": ["..."]}] }`
- `--tracked-config path/to/file.json` with `{ "tracked_repositories": ["owner/repo", ...] }`

## Local run

```bash
python scripts/repo_watch.py --output /tmp/humean-repo-watch-report.md
```

Publish/update issue:

```bash
GITHUB_TOKEN=... GITHUB_REPOSITORY=owner/repo \
python scripts/repo_watch.py --publish-issue --output /tmp/humean-repo-watch-report.md
```

## Security boundaries

- no execution of discovered repository code;
- no automatic dependency installation from discovered repositories;
- no automatic merge;
- no automatic dependency PR creation;
- no secret usage beyond `GITHUB_TOKEN`.

All integration decisions remain human-approved.
