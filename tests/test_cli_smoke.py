from __future__ import annotations

import subprocess


def test_runpilot_help_exits_zero() -> None:
    """Basic smoke test that the CLI is installed and responds."""
    result = subprocess.run(
        ["runpilot", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert "run" in result.stdout.lower()
    assert "list" in result.stdout.lower()
