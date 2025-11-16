from __future__ import annotations

from pathlib import Path

from .config import RunConfig


def run_local_container(cfg: RunConfig, run_dir: Path) -> int:
    """
    Stub implementation of the local container runner.

    For Day 2:
    - Writes a fake logs.txt file in the run directory
    - Prints what it would do
    - Returns exit code 0
    """
    log_path = run_dir / "logs.txt"

    lines = [
        f"[RunPilot] Stub run for '{cfg.name}'",
        f"Image: {cfg.image}",
        f"Entrypoint: {cfg.entrypoint}",
        "",
        "This is a stub run. No containers were actually started.",
    ]

    with log_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[RunPilot] (stub) Logs written to {log_path}")

    # Future: replace this with real Docker execution and real exit code.
    return 0
