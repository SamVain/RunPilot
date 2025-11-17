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


def parse_metrics_from_log(log_path: Path) -> Dict[str, Any]:
    """
    Parse metrics from a log file.

    Expected primary format (used in tests):

        METRIC {"step": 1, "loss": 0.92}
        METRIC {"step": 2, "loss": 0.81, "accuracy": 0.64}

    This produces a structure like:

        {
            "loss": [
                {"step": 1, "value": 0.92},
                {"step": 2, "value": 0.81},
            ],
            "accuracy": [
                {"step": 2, "value": 0.64},
            ],
            "final": {
                "loss": 0.81,
                "accuracy": 0.64,
            },
        }

    Also supports simpler key=value lines:

        METRIC loss=0.92
        METRIC loss=0.81
        METRIC accuracy=0.64

    In that case, synthetic step numbers are assigned in order of appearance.
    """
    log_path = Path(log_path)
    if not log_path.exists():
        return {}

    series: Dict[str, List[Dict[str, float]]] = {}
    global_step = 0

    try:
        with log_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("METRIC "):
                    continue

                metric_part = line[len("METRIC ") :].strip()
                if not metric_part:
                    continue

                # Case 1: JSON payload
                if metric_part.startswith("{"):
                    try:
                        import json as _json

                        payload = _json.loads(metric_part)
                        if not isinstance(payload, dict):
                            continue

                        step_val = payload.get("step")
                        try:
                            step = int(step_val)
                        except (TypeError, ValueError):
                            global_step += 1
                            step = global_step

                        for key, value in payload.items():
                            if key == "step":
                                continue
                            try:
                                val_f = float(value)
                            except (TypeError, ValueError):
                                continue
                            metric_series = series.setdefault(key, [])
                            metric_series.append({"step": step, "value": val_f})

                        continue
                    except Exception:
                        # Fall back to other parsing below
                        pass

                # Case 2: key=value format
                if "=" in metric_part:
                    name, value_str = metric_part.split("=", 1)
                    name = name.strip()
                    value_str = value_str.strip()
                    if not name:
                        continue

                    try:
                        val_f = float(value_str)
                    except ValueError:
                        continue

                    global_step += 1
                    metric_series = series.setdefault(name, [])
                    metric_series.append({"step": global_step, "value": val_f})
    except OSError:
        return {}

    # Build final dict of last values for each metric
    final: Dict[str, float] = {}
    for name, values in series.items():
        if not values:
            continue
        final[name] = values[-1]["value"]

    if final:
        result: Dict[str, Any] = dict(series)
        result["final"] = final
        return result

    return {}
