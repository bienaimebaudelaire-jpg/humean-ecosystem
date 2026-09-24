from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

STABLE_ISSUE_MARKER = "<!-- HUMEAN_REPO_WATCH_STABLE_ISSUE -->"


@dataclass(frozen=True)
class Theme:
    name: str
    query: str
    projects: tuple[str, ...]


@dataclass(frozen=True)
class RepoCandidate:
    full_name: str
    html_url: str
    description: str
    stars: int
    pushed_at: str
    license_spdx: str | None
    archived: bool
    is_fork: bool
    themes: tuple[str, ...]
    projects: tuple[str, ...]


DEFAULT_THEMES: tuple[Theme, ...] = (
    Theme(
        name="AI agents/autonomous agents",
        query="autonomous agent framework",
        projects=("HUMEAN", "Automaton", "Agent-Reach"),
    ),
    Theme(
        name="orchestration/governance",
        query="llm orchestration governance",
        projects=("humean-ecosystem", "humean-ai"),
    ),
    Theme(
        name="TypeScript/Python LLM tooling",
        query="llm tooling typescript python",
        projects=("HUMEAN", "Automaton", "humean-ai"),
    ),
    Theme(
        name="fact checking/provenance",
        query="fact checking provenance ai",
        projects=("fact-check-app", "humean-ecosystem"),
    ),
    Theme(
        name="travel planning",
        query="travel planning assistant ai",
        projects=("time-travel-companion",),
    ),
    Theme(
        name="video automation",
        query="video automation content production ai",
        projects=("laboiteaboulon", "Agent-Reach"),
    ),
)


DEFAULT_TRACKED_REPOSITORIES: tuple[str, ...] = (
    "Conway-Research/automaton",
    "bienaimebaudelaire-jpg/humean-ecosystem",
    "bienaimebaudelaire-jpg/humean-ai",
    "bienaimebaudelaire-jpg/fact-check-app",
    "bienaimebaudelaire-jpg/time-travel-companion",
    "bienaimebaudelaire-jpg/laboiteaboulon",
    "bienaimebaudelaire-jpg/Agent-Reach",
)


def parse_search_items(items: list[dict], theme: Theme) -> list[RepoCandidate]:
    parsed: list[RepoCandidate] = []
    for item in items:
        full_name = str(item.get("full_name") or "").strip()
        html_url = str(item.get("html_url") or "").strip()
        if not full_name or not html_url:
            continue

        license_data = item.get("license") or {}
        license_spdx = license_data.get("spdx_id") if isinstance(license_data, dict) else None
        if license_spdx == "NOASSERTION":
            license_spdx = None

        parsed.append(
            RepoCandidate(
                full_name=full_name,
                html_url=html_url,
                description=str(item.get("description") or "").strip(),
                stars=int(item.get("stargazers_count") or 0),
                pushed_at=str(item.get("pushed_at") or ""),
                license_spdx=license_spdx,
                archived=bool(item.get("archived")),
                is_fork=bool(item.get("fork")),
                themes=(theme.name,),
                projects=theme.projects,
            )
        )
    return parsed


def filter_candidates(
    candidates: list[RepoCandidate],
    *,
    min_stars: int,
    max_inactive_days: int,
    now: datetime | None = None,
) -> list[RepoCandidate]:
    ref = now or datetime.now(UTC)
    min_pushed_at = ref - timedelta(days=max_inactive_days)

    kept: list[RepoCandidate] = []
    for candidate in candidates:
        if candidate.archived:
            continue
        if candidate.stars < min_stars:
            continue
        if candidate.license_spdx is None:
            continue
        try:
            pushed_raw = candidate.pushed_at
            if pushed_raw.endswith("Z"):
                pushed_raw = f"{pushed_raw[:-1]}+00:00"
            pushed_at = datetime.fromisoformat(pushed_raw)
        except ValueError:
            continue
        if pushed_at < min_pushed_at:
            continue
        kept.append(candidate)
    return kept


def deduplicate_candidates(candidates: list[RepoCandidate]) -> list[RepoCandidate]:
    by_repo: dict[str, RepoCandidate] = {}
    for candidate in candidates:
        key = candidate.full_name.lower()
        existing = by_repo.get(key)
        if not existing:
            by_repo[key] = candidate
            continue

        merged_themes = tuple(sorted(set(existing.themes) | set(candidate.themes)))
        merged_projects = tuple(sorted(set(existing.projects) | set(candidate.projects)))
        better = candidate if candidate.stars > existing.stars else existing

        by_repo[key] = RepoCandidate(
            full_name=better.full_name,
            html_url=better.html_url,
            description=better.description,
            stars=max(existing.stars, candidate.stars),
            pushed_at=max(existing.pushed_at, candidate.pushed_at),
            license_spdx=existing.license_spdx or candidate.license_spdx,
            archived=existing.archived and candidate.archived,
            is_fork=existing.is_fork and candidate.is_fork,
            themes=merged_themes,
            projects=merged_projects,
        )

    return sorted(by_repo.values(), key=lambda item: item.stars, reverse=True)


def _risk_labels(candidate: RepoCandidate, tracked: set[str]) -> str:
    risks: list[str] = []
    if candidate.full_name in tracked:
        risks.append("Déjà suivi")
    if candidate.is_fork:
        risks.append("Dépôt fork")
    if (candidate.license_spdx or "").upper().startswith("GPL") or (candidate.license_spdx or "").upper().startswith("AGPL"):
        risks.append("Compatibilité licence à vérifier")
    return ", ".join(risks) if risks else "Validation sécurité/humaine requise"


def suggested_action(candidate: RepoCandidate, tracked: set[str]) -> str:
    if candidate.full_name in tracked:
        return "observer"
    if candidate.is_fork:
        return "ne pas intégrer"
    if candidate.stars >= 500:
        return "tester en sandbox"
    return "ouvrir une issue"


def build_report_markdown(
    candidates: list[RepoCandidate],
    *,
    tracked_repositories: tuple[str, ...],
    generated_at: datetime | None = None,
    max_rows: int = 20,
) -> str:
    generated = generated_at or datetime.now(UTC)
    tracked = set(tracked_repositories)

    lines: list[str] = [
        f"{STABLE_ISSUE_MARKER}",
        "# Veille GitHub publique",
        "",
        f"- Date (UTC): {generated.isoformat()}",
        "- Source: API GitHub (publique/authentifiée via `GITHUB_TOKEN`)",
        "- Règle: aucune exécution de code distant, aucune installation automatique, aucune fusion automatique.",
        "",
        "## Dépôts déjà suivis",
        "",
    ]
    for repo in tracked_repositories:
        lines.append(f"- `{repo}`")

    lines.extend(
        [
            "",
            "## Recommandations",
            "",
            "| Dépôt | Raison de pertinence | Activité | Licence | Risques | Projet(s) concerné(s) | Action proposée | Liens GitHub |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )

    for candidate in candidates[:max_rows]:
        relevance = " ; ".join(candidate.themes)
        activity = f"⭐ {candidate.stars} · pushed {candidate.pushed_at[:10]}"
        license_name = candidate.license_spdx or "Inconnue"
        risks = _risk_labels(candidate, tracked)
        projects = ", ".join(candidate.projects)
        action = suggested_action(candidate, tracked)
        lines.append(
            "| "
            f"`{candidate.full_name}` | {relevance} | {activity} | {license_name} | {risks} | {projects} | {action} | [Repo]({candidate.html_url}) |"
        )

    lines.extend(
        [
            "",
            "## Section sécurité",
            "",
            "- Aucun code des dépôts découverts n'est exécuté.",
            "- Aucune dépendance n'est installée automatiquement.",
            "- Aucune pull request de dépendance n'est créée automatiquement.",
            "- Aucun merge automatique n'est effectué.",
            "- Aucun secret autre que `GITHUB_TOKEN` n'est utilisé.",
            "- Toute intégration reste soumise à approbation humaine.",
        ]
    )

    return "\n".join(lines).strip() + "\n"
