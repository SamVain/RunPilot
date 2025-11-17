import os
from pathlib import Path

DEFAULT_BASE_DIR = Path(os.environ.get("RUNPILOT_HOME", "~/.runpilot")).expanduser()
RUNS_DIR = DEFAULT_BASE_DIR / "runs"


def get_run_dir(run_id: str) -> Path:
    return RUNS_DIR / run_id