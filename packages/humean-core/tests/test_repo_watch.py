from datetime import UTC, datetime

from humean_core.repo_watch import (
    DEFAULT_TRACKED_REPOSITORIES,
    Theme,
    build_report_markdown,
    deduplicate_candidates,
    filter_candidates,
    parse_search_items,
)


def _theme() -> Theme:
    return Theme(name="AI agents/autonomous agents", query="autonomous agent", projects=("HUMEAN", "Automaton"))


def test_parse_search_items_ignores_invalid_records():
    items = [
        {
            "full_name": "org/repo-a",
            "html_url": "https://github.com/org/repo-a",
            "description": "A",
            "stargazers_count": 120,
            "pushed_at": "2026-09-20T00:00:00Z",
            "license": {"spdx_id": "MIT"},
            "archived": False,
            "fork": False,
        },
        {
            "full_name": "",
            "html_url": "https://github.com/org/repo-b",
        },
    ]

    parsed = parse_search_items(items, _theme())

    assert len(parsed) == 1
    assert parsed[0].full_name == "org/repo-a"
    assert parsed[0].themes == ("AI agents/autonomous agents",)


def test_filter_candidates_enforces_activity_popularity_and_license():
    parsed = parse_search_items(
        [
            {
                "full_name": "org/active",
                "html_url": "https://github.com/org/active",
                "stargazers_count": 100,
                "pushed_at": "2026-09-10T00:00:00Z",
                "license": {"spdx_id": "MIT"},
                "archived": False,
                "fork": False,
            },
            {
                "full_name": "org/no-license",
                "html_url": "https://github.com/org/no-license",
                "stargazers_count": 100,
                "pushed_at": "2026-09-10T00:00:00Z",
                "license": {"spdx_id": "NOASSERTION"},
                "archived": False,
                "fork": False,
            },
            {
                "full_name": "org/archived",
                "html_url": "https://github.com/org/archived",
                "stargazers_count": 100,
                "pushed_at": "2026-09-10T00:00:00Z",
                "license": {"spdx_id": "MIT"},
                "archived": True,
                "fork": False,
            },
            {
                "full_name": "org/old",
                "html_url": "https://github.com/org/old",
                "stargazers_count": 100,
                "pushed_at": "2024-01-01T00:00:00Z",
                "license": {"spdx_id": "MIT"},
                "archived": False,
                "fork": False,
            },
            {
                "full_name": "org/low-stars",
                "html_url": "https://github.com/org/low-stars",
                "stargazers_count": 2,
                "pushed_at": "2026-09-10T00:00:00Z",
                "license": {"spdx_id": "MIT"},
                "archived": False,
                "fork": False,
            },
        ],
        _theme(),
    )

    kept = filter_candidates(
        parsed,
        min_stars=40,
        max_inactive_days=180,
        now=datetime(2026, 9, 24, tzinfo=UTC),
    )

    assert [item.full_name for item in kept] == ["org/active"]


def test_deduplicate_candidates_merges_themes_and_projects():
    theme_a = Theme(name="AI agents/autonomous agents", query="x", projects=("HUMEAN",))
    theme_b = Theme(name="video automation", query="y", projects=("laboiteaboulon",))

    first = parse_search_items(
        [
            {
                "full_name": "org/repo",
                "html_url": "https://github.com/org/repo",
                "stargazers_count": 50,
                "pushed_at": "2026-09-01T00:00:00Z",
                "license": {"spdx_id": "MIT"},
                "archived": False,
                "fork": False,
            }
        ],
        theme_a,
    )
    second = parse_search_items(
        [
            {
                "full_name": "org/repo",
                "html_url": "https://github.com/org/repo",
                "stargazers_count": 70,
                "pushed_at": "2026-09-15T00:00:00Z",
                "license": {"spdx_id": "MIT"},
                "archived": False,
                "fork": False,
            }
        ],
        theme_b,
    )

    deduped = deduplicate_candidates(first + second)

    assert len(deduped) == 1
    assert deduped[0].stars == 70
    assert deduped[0].themes == ("AI agents/autonomous agents", "video automation")
    assert deduped[0].projects == ("HUMEAN", "laboiteaboulon")


def test_build_report_markdown_contains_required_columns_and_actions():
    candidate = parse_search_items(
        [
            {
                "full_name": "Conway-Research/automaton",
                "html_url": "https://github.com/Conway-Research/automaton",
                "description": "agent runtime",
                "stargazers_count": 900,
                "pushed_at": "2026-09-22T00:00:00Z",
                "license": {"spdx_id": "MIT"},
                "archived": False,
                "fork": False,
            }
        ],
        _theme(),
    )[0]

    report = build_report_markdown(
        [candidate],
        tracked_repositories=DEFAULT_TRACKED_REPOSITORIES,
        generated_at=datetime(2026, 9, 24, tzinfo=UTC),
        max_rows=10,
    )

    assert "| Dépôt | Raison de pertinence | Activité | Licence | Risques | Projet(s) concerné(s) | Action proposée | Liens GitHub |" in report
    assert "Conway-Research/automaton" in report
    assert "observer" in report
    assert "## Section sécurité" in report
