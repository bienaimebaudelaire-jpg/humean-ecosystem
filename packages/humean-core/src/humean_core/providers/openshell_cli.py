"""Typed, shell-safe helpers for invoking the OpenShell CLI."""

from __future__ import annotations

import math
import subprocess
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

# Informational commands only. Anything that can create, change or delete state
# must be allowed explicitly by the caller through ``allowed_commands``.
DEFAULT_ALLOWED_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("--help",),
    ("--version",),
    ("sandbox", "--help"),
)


class OpenShellError(RuntimeError):
    """Raised when the OpenShell CLI cannot complete a command."""


class OpenShellCommandNotAllowedError(ValueError):
    """Raised when a command is not covered by the allowlist."""


@dataclass(frozen=True)
class OpenShellResult:
    stdout: str
    stderr: str
    returncode: int


def run_openshell_command(
    args: Sequence[str],
    *,
    timeout: float = 30.0,
    executable: str = "openshell",
    allowed_commands: Iterable[Sequence[str]] = DEFAULT_ALLOWED_COMMANDS,
) -> OpenShellResult:
    """Run a non-interactive OpenShell CLI command without invoking a shell.

    ``args`` must start with one of the ``allowed_commands`` prefixes (default:
    informational commands only). Pass an explicit allowlist to enable more; never
    build it from model or user input.
    """
    if isinstance(args, (str, bytes)) or not args:
        raise ValueError("args must be a non-empty sequence of strings")
    if any(not isinstance(arg, str) or "\0" in arg for arg in args):
        raise ValueError("args must contain only strings without null bytes")
    args = tuple(args)
    allowed = [tuple(prefix) for prefix in allowed_commands]
    if not any(prefix and args[: len(prefix)] == prefix for prefix in allowed):
        raise OpenShellCommandNotAllowedError(
            "OpenShell command is not in the allowlist"
        )
    if not executable or "\0" in executable:
        raise ValueError("executable must be a non-empty string without null bytes")
    if isinstance(timeout, bool) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be a finite positive number")

    try:
        result = subprocess.run(
            [executable, *args],
            capture_output=True,
            check=False,
            shell=False,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise OpenShellError(
            "OpenShell CLI was not found; install it and ensure it is on PATH"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise OpenShellError(
            f"OpenShell command timed out after {timeout} seconds"
        ) from exc
    except OSError as exc:
        raise OpenShellError("Unable to start the OpenShell CLI") from exc

    if result.returncode != 0:
        raise OpenShellError(
            f"OpenShell command failed with exit code {result.returncode}"
        )
    return OpenShellResult(
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=result.returncode,
    )
