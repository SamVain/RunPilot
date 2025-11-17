from __future__ import annotations

from typing import Any, Dict

from .metrics import read_metrics
from .paths import get_run_dir


def print_summary_table(summary: Dict[str, Any]) -> None:
    if not summary:
        print("No summary metrics recorded.")
        return

    # Very simple table
    key_width = max(len(k) for k in summary.keys())
    print("Summary metrics:")
    for key, value in summary.items():
        print(f"  {key.ljust(key_width)}  {value}")


def metrics_command(run_id: str, json_output: bool = False) -> int:
    """
    Entry point for `runpilot metrics <run-id>`.
    Returns 0 on success, non zero on error.
    """
    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        print(f"Run directory not found for id: {run_id}")
        return 1

    data = read_metrics(run_dir)
    if data is None:
        print(f"No metrics.json found for run {run_id}.")
        return 1

    if json_output:
        import json as _json
        print(_json.dumps(data, indent=2, sort_keys=True))
        return 0

    summary = data.get("summary") or {}
    print_summary_table(summary)
    return 0