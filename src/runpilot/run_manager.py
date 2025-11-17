from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .metrics import write_metrics


def finalise_run(run_dir: Path, run_record: Dict[str, Any]) -> None:
    """
    Called when a run finishes. Persist run.json and emit metrics.json.

    This helper is not currently wired into the CLI, but can be used
    by higher level orchestration later.
    """
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    # Write run.json
    run_json_path = run_dir / "run.json"
    run_json_path.write_text(
        json.dumps(run_record, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    # Build a basic summary for metrics.json
    run_id = run_record.get("id") or run_dir.name
    exit_code = run_record.get("exit_code", 0)
    started_at = run_record.get("started_at")
    finished_at = run_record.get("finished_at")

    duration_seconds: float | None = None
    if started_at and finished_at:
        try:
            start_dt = datetime.fromisoformat(started_at)
            end_dt = datetime.fromisoformat(finished_at)
            duration_seconds = (end_dt - start_dt).total_seconds()
        except ValueError:
            duration_seconds = None

    summary: Dict[str, float] = {}

    if duration_seconds is not None:
        summary["duration_seconds"] = float(duration_seconds)

    try:
        summary["exit_code"] = float(exit_code)
    except (TypeError, ValueError):
        pass

    tags = run_record.get("tags") or []

    if summary:
        write_metrics(run_dir=run_dir, run_id=run_id, summary=summary, tags=tags)
