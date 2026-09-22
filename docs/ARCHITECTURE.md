# Architecture

## Naming

**RouteCore** is this repository's internal execution planner and router
(`humean_core.router`, `humean_core.run_task`) — it has no third-party
dependency. **OmniRoute** ([github.com/diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute))
is an unrelated, optional third-party self-hosted gateway that RouteCore
may delegate execution to for a subset of capabilities (see "Provider
execution backend" below and `humean_core.providers.omniroute_gateway`).
The two names are easy to conflate because RouteCore can route *to*
OmniRoute, but they are separate systems: RouteCore is the generic
infrastructure defined here; OmniRoute is one optional, pluggable executor
among several.

## Boundaries

```text
Application → HUMEAN contract → RouteCore → Capability Registry → Provider/tool
                         │                │
                         ├─ policy        └─ evidence/provenance
                         ├─ audit
                         └─ human gate
```

HUMEAN is the control and accountability layer. RouteCore is the execution planner and router. Applications own their domain rules and user experience.

## Core domain objects

- **Task**: user or system request with constraints and risk level.
- **Capability**: a registered model, tool, source, or agent ability.
- **Route**: selected ordered capabilities and the reason for selection.
- **Evidence**: source, timestamp, confidence, and provenance attached to claims.
- **Decision**: result, uncertainty, policy outcome, and audit reference.
- **RegistryDiff**: proposed change to a capability, never an implicit mutation.

## Routing lifecycle

1. Normalize a task and classify its risk.
2. Resolve required capabilities.
3. Filter by status, policy, privacy, budget, and availability.
4. Score candidates using observed reliability, quality, cost, and latency.
5. Execute with bounded retries and timeouts.
6. Validate output and collect evidence.
7. Request human approval when policy requires it.
8. Write an audit event and performance record.

## Self-update lifecycle

The environment watcher may read explicitly configured provider documentation and public sources. It creates a structured diff. Low-impact, high-confidence metadata changes may be auto-approved only after that policy is explicitly enabled; provider access, routing policy, cost limits, and user-impacting changes require human approval.

## Non-goals

- no autonomous code rewriting;
- no quota circumvention or key farming;
- no hidden provider switching for high-impact tasks;
- no claim that a response is verified without evidence;
- no broad application logic inside the generic core.

## Provider execution backend

RouteCore may delegate provider execution to a self-hosted instance of the
open-source **OmniRoute** gateway (github.com/diegosouzapw/OmniRoute) for
free-tier-aware multi-provider access. Its terms-risk catalog (ok / caution /
ambiguous / avoid per provider) is treated as an input constraint, consistent
with the non-goal below of never circumventing quotas or farming keys.
