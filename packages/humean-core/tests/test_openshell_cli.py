from __future__ import annotations

import subprocess

import pytest
from humean_core.providers.openshell_cli import (
    OpenShellError,
    OpenShellResult,
    run_openshell_command,
)


def test_run_openshell_command_invokes_cli_without_a_shell(monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="ready\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_openshell_command(["sandbox", "--help"], timeout=12)

    assert result == OpenShellResult(stdout="ready\n", stderr="", returncode=0)
    assert calls == [
        (
            ["openshell", "sandbox", "--help"],
            {
                "capture_output": True,
                "check": False,
                "shell": False,
                "text": True,
                "timeout": 12,
            },
        )
    ]


@pytest.mark.parametrize("args", ["--help", [], ["bad\0arg"]])
def test_run_openshell_command_rejects_invalid_arguments(args):
    with pytest.raises(ValueError):
        run_openshell_command(args)


@pytest.mark.parametrize("timeout", [0, -1, float("inf"), float("nan"), True])
def test_run_openshell_command_rejects_invalid_timeout(timeout):
    with pytest.raises(ValueError, match="timeout"):
        run_openshell_command(["--help"], timeout=timeout)


def test_run_openshell_command_reports_missing_cli(monkeypatch):
    def fake_run(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(OpenShellError, match="not found"):
        run_openshell_command(["--help"])


def test_run_openshell_command_reports_timeout(monkeypatch):
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired("openshell", timeout=1)

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(OpenShellError, match="timed out"):
        run_openshell_command(["--help"], timeout=1)


def test_run_openshell_command_reports_nonzero_exit(monkeypatch):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(
            command, 2, stdout="", stderr="sensitive output"
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(OpenShellError, match="exit code 2") as exc_info:
        run_openshell_command(["sandbox", "list"])

    assert "sensitive output" not in str(exc_info.value)
