"""Typed, shell-safe helpers for invoking the OpenShell CLI."""

from __future__ import annotations

import math
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass


class OpenShellError(RuntimeError):
    """Raised when the OpenShell CLI cannot complete a command."""


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
) -> OpenShellResult:
    """Run a non-interactive OpenShell CLI command without invoking a shell."""
    if isinstance(args, (str, bytes)) or not args:
        raise ValueError("args must be a non-empty sequence of strings")
    if any(not isinstance(arg, str) or "\0" in arg for arg in args):
        raise ValueError("args must contain only strings without null bytes")
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
