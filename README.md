# HUMEAN Ecosystem

HUMEAN and OmniRoute infrastructure for governed AI orchestration, capability evaluation, and focused applications.

## Vision

- **HUMEAN** provides memory, evaluation, governance, risk controls, audit, and human approval.
- **OmniRoute** decomposes tasks and routes them to suitable models, agents, tools, and sources.
- **SaveMoneyReminder (SMV)** is the first concrete application.
- **Time & Travel** is a future focused application, currently at the specification stage.

The infrastructure stays generic and invisible to end users. Applications remain intentionally narrow: one domain, one audience, one measurable value proposition.

## Status

This repository is a clean foundation. It contains architecture documents, initial contracts, a capability probe, and a minimal registry schema. It does not yet claim production-ready orchestration.

## Repository layout

```text
humean-ecosystem/
├── apps/                    # Focused products and integration contracts
├── docs/                    # Architecture and product decisions
├── packages/humean-core/    # Generic HUMEAN/OmniRoute domain package
├── schemas/                 # Database and event schemas
├── scripts/                 # Local operational tools
└── tests/                   # Cross-package tests
```

## Principles

1. No silent self-modification: environment changes produce proposed diffs.
2. Human approval is required for high-impact or low-confidence changes.
3. Providers are interchangeable; credentials never live in source code.
4. Evidence, provenance, uncertainty, cost, latency, and reliability are first-class data.
5. No new application domain until an existing product has real users.

## First steps

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
pytest

# Optional capability probe; configure keys in .env first
python scripts/capability_probe.py --prompt "Explain subscription comparison in two sentences."
```

See [HUMEAN_ECOSYSTEM_SUMMARY.md](HUMEAN_ECOSYSTEM_SUMMARY.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and [docs/PRODUCT_BOUNDARIES.md](docs/PRODUCT_BOUNDARIES.md).

## Legacy reference

The former `humean-ai` repository is retained as historical prototype material. Its configuration and experimental provider code must be reviewed before selective migration; it is not copied wholesale into this repository.

## License

AGPL-3.0-or-later.
