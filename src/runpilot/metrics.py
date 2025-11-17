from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def parse_metrics_from_log(log_path: Path) -> Dict[str, Any]:
    """
    Parse metrics from a log file.

    Convention:
      Any line starting with 'METRIC ' is treated as JSON.
      Example:
        METRIC {"step": 1, "loss": 0.92}
        METRIC {"step": 2, "loss": 0.81, "accuracy": 0.64}

    Returns a dict of the form:
      {
        "loss": [
          {"step": 1, "value": 0.92},
          {"step": 2, "value": 0.81}
        ],
        "accuracy": [
          {"step": 2, "value": 0.64}
        ],
        "final": {
          "loss": 0.81,
          "accuracy": 0.64
        }
      }
    """
    if not log_path.is_file():
        return {}

    series: Dict[str, List[Dict[str, Any]]] = {}
    final_values: Dict[str, Any] = {}

    try:
        raw = log_path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return {}

    for idx, line in enumerate(raw, start=1):
        line = line.strip()
        if not line.startswith("METRIC "):
            continue

        payload = line[len("METRIC ") :].strip()
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            continue

        if not isinstance(data, dict):
            continue

        step = data.get("step", idx)

        for key, value in data.items():
            if key == "step":
                continue
            series.setdefault(key, []).append({"step": step, "value": value})
            final_values[key] = value

    if not series:
        return {}

    return {
        **{k: v for k, v in series.items()},
        "final": final_values,
    }


def write_metrics(run_dir: Path, metrics: Dict[str, Any]) -> None:
    """
    Write metrics.json into the run directory if there are metrics.
    """
    if not metrics:
        return

    metrics_path = run_dir / "metrics.json"
    metrics_path.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )
