from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

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
    Example: 20251119T142355Z-hello-run
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
    Example: ~/.runpilot/runs/20251119T142355Z-hello-run
    """
    runs_dir = get_runs_dir()
    run_id = _generate_run_id(name)
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=False, exist_ok=False)
    return run_dir


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_existing_metadata(meta_path: Path) -> Dict[str, Any]:
    if not meta_path.is_file():
        return {}
    try:
        with meta_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        # If metadata is corrupt, start fresh rather than crashing.
        return {}


def write_run_metadata(
    run_dir: Path,
    cfg: RunConfig,
    status: str,
    exit_code: Optional[int] = None,
) -> None:
    """
    Create or update the metadata file for a run.

    Fields:
      id          run directory name
      run_dir     absolute path to the run directory
      name        run name from config
      image       container image
      entrypoint  command to run inside the container
      status      pending, finished, failed
      created_at  first time metadata was written
      finished_at set when status is finished or failed
      exit_code   numeric exit code if known
    """
    meta_path = run_dir / "run.json"
    meta = _load_existing_metadata(meta_path)

    # Core identity
    meta["id"] = run_dir.name
    meta["run_dir"] = str(run_dir)

    # Config fields
    meta["name"] = cfg.name
    meta["image"] = cfg.image
    meta["entrypoint"] = cfg.entrypoint

    # Status
    meta["status"] = status

    # Timestamps
    if "created_at" not in meta:
        meta["created_at"] = _now_iso()

    if exit_code is not None:
        meta["exit_code"] = exit_code

    if status in {"finished", "failed"}:
        meta["finished_at"] = _now_iso()

    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def load_all_runs() -> list[Dict[str, Any]]:
    """
    Load metadata for all runs under the runs directory.

    Returns a list of dicts sorted by created_at descending if present,
    otherwise sorted by id descending.
    """
    runs_dir = get_runs_dir()
    results: list[Dict[str, Any]] = []

    if not runs_dir.is_dir():
        return results

    for child in runs_dir.iterdir():
        if not child.is_dir():
            continue
        meta_path = child / "run.json"
        if not meta_path.is_file():
            continue
        try:
            with meta_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                continue
        except Exception:
            continue

        # Ensure id and run_dir are always present
        data.setdefault("id", child.name)
        data.setdefault("run_dir", str(child))
        results.append(data)

    def sort_key(item: Dict[str, Any]) -> str:
        return str(item.get("created_at") or item.get("id") or "")

    results.sort(key=sort_key, reverse=True)
    return results


def load_run(run_id: str) -> Dict[str, Any]:
    """
    Load metadata for a single run by id.

    Raises FileNotFoundError if the run or metadata file does not exist.
    """
    run_dir = get_runs_dir() / run_id
    meta_path = run_dir / "run.json"

    if not meta_path.is_file():
        raise FileNotFoundError(f"Run '{run_id}' not found")

    with meta_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Metadata for run '{run_id}' is not a JSON object")

    data.setdefault("id", run_id)
    data.setdefault("run_dir", str(run_dir))
    return data
