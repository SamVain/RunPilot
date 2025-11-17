from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


METRICS_FILENAME = "metrics.json"


@dataclass
class Metrics:
    run_id: str
    summary: Dict[str, float]
    time_series: Dict[str, List[float]] | None = None
    tags: List[str] | None = None
    recorded_at: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if not self.recorded_at:
            data["recorded_at"] = datetime.now(timezone.utc).isoformat()
        return data


def metrics_path(run_dir: Path) -> Path:
    return run_dir / METRICS_FILENAME


def write_metrics(
    run_dir: Path,
    run_id: str,
    summary: Dict[str, float],
    time_series: Dict[str, List[float]] | None = None,
    tags: List[str] | None = None,
) -> Path:
    """Write metrics.json into the run directory."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    metrics = Metrics(
        run_id=run_id,
        summary=summary,
        time_series=time_series,
        tags=tags,
    )

    path = metrics_path(run_dir)
    with path.open("w", encoding="utf-8") as f:
        json.dump(metrics.to_dict(), f, indent=2, sort_keys=True)

    return path


def read_metrics(run_dir: Path) -> Optional[Dict[str, Any]]:
    """Return metrics.json as a dict, or None if missing or invalid."""
    path = metrics_path(Path(run_dir))
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def parse_metrics_from_log(log_path: Path) -> Dict[str, float]:
    """
    Very simple placeholder implementation.

    Reads the log file and looks for lines of the form:

        METRIC name=value

    For example:

        METRIC train_loss=0.1234
        METRIC accuracy=0.987

    Returns a dict like {"train_loss": 0.1234, "accuracy": 0.987}.

    If no metrics are found, returns an empty dict.
    """
    log_path = Path(log_path)
    if not log_path.exists():
        return {}

    summary: Dict[str, float] = {}

    try:
        with log_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("METRIC "):
                    continue

                # Remove "METRIC " prefix
                metric_part = line[len("METRIC ") :]

                if "=" not in metric_part:
                    continue

                name, value_str = metric_part.split("=", 1)
                name = name.strip()
                value_str = value_str.strip()

                try:
                    value = float(value_str)
                except ValueError:
                    continue

                summary[name] = value
    except OSError:
        return {}

    return summary
