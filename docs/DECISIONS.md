# Architecture decisions

## ADR-0001: Start a clean ecosystem repository

The former `humean-ai` repository remains legacy reference material. The new repository avoids copying experimental code and makes the infrastructure/application boundary explicit.

## ADR-0002: Proposal-based self-update

External changes create registry diffs. Critical routing, credentials, policy, and cost changes require a human gate. This prevents silent self-modification while retaining environmental adaptability.

## ADR-0003: Legitimate quota usage only

Free tiers, local models, caching, and provider routing may reduce cost when used within provider terms. Multiple-account or key-rotation schemes intended to bypass limits are not a platform design principle.

## ADR-0004: SMV first

SMV is the most mature application and supplies the first realistic integration scenario. Time & Travel remains deliberately narrow until its data and source contracts are implemented.
