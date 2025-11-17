from __future__ import annotations

import subprocess
from pathlib import Path

from .config import RunConfig


def run_local_container(cfg: RunConfig, run_dir: Path) -> int:
    """
    Local container runner using Docker with a mounted run directory.

    Behaviour:
      • If Docker is available, run the configured image and entrypoint.
      • Mount run_dir into the container at /run.
      • Capture stdout and stderr into logs.txt.
      • Return the container exit code.
      • If Docker is not available, write a stub log and return 1.
    """
    log_path = run_dir / "logs.txt"

    # Build Docker command:
    # docker run --rm -v <run_dir>:/run -w /run <image> sh -lc "<entrypoint>"
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{run_dir}:/run",
        "-w",
        "/run",
        cfg.image,
        "sh",
        "-lc",
        cfg.entrypoint,
    ]

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        output = proc.stdout or ""
        exit_code = proc.returncode
    except FileNotFoundError:
        # Docker binary not found
        output = (
            "[RunPilot] Docker is not installed or not on PATH.\n"
            "[RunPilot] Cannot execute container run.\n"
            f"Requested image: {cfg.image}\n"
            f"Entrypoint: {cfg.entrypoint}\n"
        )
        exit_code = 1

    # Write logs regardless of success or failure
    with log_path.open("w", encoding="utf-8") as f:
        f.write(output)

    print(f"[RunPilot] Logs written to {log_path}")
    if exit_code != 0:
        print(f"[RunPilot] Container exited with code {exit_code}")

    return exit_code
