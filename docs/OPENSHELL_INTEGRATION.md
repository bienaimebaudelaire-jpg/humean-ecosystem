# OpenShell runtime integration design

NVIDIA [OpenShell](https://github.com/NVIDIA/OpenShell) is an optional,
recommended secure runtime backend for executing autonomous agents. This page
defines an integration contract for HUMEAN/RouteCore; it is not an OpenShell
configuration, a hard dependency, or a commitment to a specific SDK. HUMEAN
must remain neutral across runtime and provider implementations.

## Python CLI wrapper

The Python integration is optional. Install its SDK extra with
`pip install -e '.[openshell]'`; install and configure the OpenShell CLI and
gateway separately, following the [official installation guide](https://docs.nvidia.com/openshell/latest/about/installation).
Use a matching CLI, gateway, and SDK release when possible.

The typed `humean_core.providers.openshell_cli.run_openshell_command` helper
invokes the CLI using an argument list (never a shell), captures output, and
raises `OpenShellError` if the CLI is missing, times out, or exits unsuccessfully:

```python
from humean_core.providers.openshell_cli import run_openshell_command

result = run_openshell_command(["sandbox", "--help"], timeout=10)
print(result.stdout)
```

Commands are checked against an allowlist of argument prefixes. By default only
informational commands are accepted (`--help`, `--version`, `sandbox --help`);
anything else raises `OpenShellCommandNotAllowedError`. Enable more commands
explicitly, with a fixed list defined in code and never built from model or user
input:

```python
run_openshell_command(["sandbox", "list"], allowed_commands=[("sandbox", "list")])
```

The result exposes `stderr`, which may contain sensitive data: do not log it
verbatim.

Only use this helper for non-interactive CLI commands. It does not install or
start OpenShell, create a sandbox automatically, or replace HUMEAN policy and
human approval. Avoid passing credentials as command-line arguments; use
OpenShell's configured credential and secret mechanisms instead.

OpenShell provides isolated agent sandboxes, runtime policy enforcement for
files, processes, and network connections, provider credentials restricted to
approved endpoints, and policy-change verification before approval. Its
gateway can manage sandboxes and access, with Kubernetes deployment available.
These controls complement HUMEAN's orchestration and governance; they do not
replace application authorization, human review, or audit.

## Concept mapping

| HUMEAN/RouteCore concept | OpenShell integration |
| --- | --- |
| Capability registry | Register an agent-execution capability whose declared sandbox/runtime capabilities are limited by both HUMEAN policy and the runtime policy. |
| Provider abstraction | Map HUMEAN provider aliases to OpenShell providers and explicitly approved endpoints. Keep credentials in the runtime/deployment secret store. |
| Governance and audit | Represent provider, credential, and policy changes as HUMEAN proposals. Verify policy changes, require human approval for high-impact changes, and retain linked HUMEAN and runtime audit references. |
| Routing | RouteCore selects an eligible execution capability; the OpenShell gateway/provider layer handles the configured provider route. Record the selected capability and routing rationale in HUMEAN's decision/audit trail. |
| Environment watch | Convert relevant public provider/runtime changes into proposed registry or policy/configuration diffs; never silently change active access or routing. |

The existing `Capability.metadata` JSON object is the extension point for
runtime-specific details. `schemas/capabilities.example.json` includes a
candidate example. Its `runtime` keys are illustrative HUMEAN metadata, not an
OpenShell-native schema or a promise that a particular SDK accepts those
fields.

## Security and approval boundaries

- Apply least privilege: define the sandbox's required file, process, and
  network access explicitly, and review the effective policy before enabling
  an agent. Treat sandboxing as defense in depth, not a replacement for
  application-level authorization.
- Keep provider credentials in the runtime or deployment secret manager. Use
  references in HUMEAN metadata only; never commit credential values, expose
  them to agent prompts or files, or include them in logs. Restrict credential
  use to approved provider endpoints.
- Changes to credentials, endpoints, provider access, sandbox permissions,
  routing, or cost limits are high impact: propose them, verify the resulting
  policy, and require explicit human approval before activation. Record who
  approved the change and its audit reference.
- Preserve provider neutrality. OpenShell is one pluggable runtime backend;
  provider aliases and capability contracts must not require NVIDIA-specific
  models or services.

## Failure and degraded mode

If the runtime, gateway, policy verification, or audit path is unavailable,
do not bypass the sandbox or silently route to a different provider/runtime.
Stop execution for tasks that require the unavailable control, or use only a
pre-approved, equivalently constrained fallback for tasks whose policy permits
it. Mark the decision as degraded, retain the failure reason without secrets,
and require human review before any change to the fallback or policy.

## Adoption path

1. Define a generic HUMEAN agent-execution capability and a least-privilege
   sandbox profile; begin with non-sensitive, low-impact tasks.
2. For SMV, assess an isolated execution boundary for generic offer-comparison
   or evidence-enrichment tasks. Keep product rules, data, and implementation
   in the private application.
3. For Time & Travel, assess a sandbox for narrow, verified local scenarios
   before considering broader provider access. Keep application-specific
   sources, data, and logic outside this repository.
4. Evaluate policy behavior, audit linkage, endpoint restrictions, failure
   handling, operational cost, and deployment support before approving broader
   use. Promote a candidate only through the existing review process.

## References

- [OpenShell repository and overview](https://github.com/NVIDIA/OpenShell)
- [OpenShell policies](https://docs.nvidia.com/openshell/latest/how-it-works/policies/overview)
- [OpenShell providers](https://docs.nvidia.com/openshell/latest/how-it-works/providers/overview)
- [OpenShell gateways](https://docs.nvidia.com/openshell/latest/how-it-works/gateways/overview)
- [HUMEAN architecture](ARCHITECTURE.md)
