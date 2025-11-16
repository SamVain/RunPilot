from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

import json

from .config import RunConfig

_ROOT_DIR_NAME = ".runpilot"
_RUNS_DIR_NAME = "runs"


def get_root_dir() -> Path:
    """
    Return the root directory for all RunPilot data.
    Example: /home/sam/.runpilot
    """
    return Path.home() / _ROOT_DIR_NAME


def get_runs_dir() -> Path:
    """
    Return the directory where all runs are stored.
    Creates it if it does not exist.
    Example: /home/sam/.runpilot/runs
    """
    runs_dir = get_root_dir() / _RUNS_DIR_NAME
    runs_dir.mkdir(parents=True, exist_ok=True)
    return runs_dir


def _generate_run_id(name: str) -> str:
    """
    Generate a simple run id from timestamp and a slug of the run name.
    Example: 20250119T142355Z-hello-run
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe = "".join(
        c if c.isalnum() or c in "-_" else "-"
        for c in name.lower()
    )
    safe = safe.strip("-_") or "run"
    safe = safe[:40]
    return f"{timestamp}-{safe}"


def create_run_dir(name: str) -> Path:
    """
    Create a new run directory and return its path.
    Example: ~/.runpilot/runs/20250119T142355Z-hello-run
    """
    runs_dir = get_runs_dir()
    run_id = _generate_run_id(name)
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=False, exist_ok=False)
    return run_dir


def _build_metadata(cfg: RunConfig, status: str) -> Dict[str, Any]:
    return {
        "name": cfg.name,
        "image": cfg.image,
        "entrypoint": cfg.entrypoint,
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def write_run_metadata(run_dir: Path, cfg: RunConfig, status: str) -> None:
    """
    Write or overwrite run metadata file in the run directory.
    """
    meta_path = run_dir / "run.json"
    meta = _build_metadata(cfg, status=status)

    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
