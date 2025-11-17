from __future__ import annotations

import os
from pathlib import Path


def get_base_dir() -> Path:
    """
    Return the base directory for RunPilot data.

    Uses RUNPILOT_HOME if set, otherwise ~/.runpilot.
    Evaluated at call time so tests can override it with environment variables.
    """
    return Path(os.environ.get("RUNPILOT_HOME", "~/.runpilot")).expanduser()


def get_runs_dir() -> Path:
    """
    Return the directory that contains all runs.
    """
    return get_base_dir() / "runs"


def get_run_dir(run_id: str) -> Path:
    """
    Return the directory path for a specific run id.
    """
    return get_runs_dir() / run_id
