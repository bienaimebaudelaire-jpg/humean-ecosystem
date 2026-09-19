# HUMEAN Ecosystem

This repository contains the generic infrastructure layer for HUMEAN and RouteCore.

It is intentionally public and focused on:
- generic orchestration contracts;
- capability registry design;
- provider abstraction;
- routing logic;
- governance and audit model;
- environment/watch and proposal-based updates.

It does not contain product-specific application code for private projects or production products.

## Project boundary

The public repository intentionally excludes:
- private application code;
- business-specific product logic;
- repositories or datasets tied to private product work;
- production pricing, customer flows, or sensitive operational data.

## Repository scope

```text
humean-ecosystem/
├── docs/
├── packages/humean-core/
├── schemas/
├── scripts/
├── tests/
└── README.md
```

## Principles

1. Generic infrastructure first.
2. Applications remain out-of-scope until they are mature and need explicit integration.
3. Provider changes are proposals, not silent mutations.
4. Human approval remains required for high-impact policy or routing decisions.
5. Security, provenance, and audit are first-class concerns.

## Historical reference

A historical configuration reference from the earlier prototype remains in `docs/archive/legacy_humean_config.json` and should be treated as legacy context only.
