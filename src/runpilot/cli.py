from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .runner import run_local_container
from .storage import create_run_dir, write_run_metadata


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="runpilot",
        description="RunPilot - reproducible AI training runner",
    )

    subparsers = parser.add_subparsers(dest="command")

    # run subcommand
    run_parser = subparsers.add_parser(
        "run",
        help="Run a training job from a config file",
    )
    run_parser.add_argument(
        "config_path",
        type=str,
        help="Path to the run config YAML file",
    )

    # list subcommand (stub for now)
    subparsers.add_parser(
        "list",
        help="List recorded runs (placeholder for now)",
    )

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "run":
        _handle_run_command(Path(args.config_path))
    elif args.command == "list":
        _handle_list_command()
    else:
        parser.print_help()


def _handle_run_command(config_path: Path) -> None:
    cfg = load_config(config_path)
    print(
        f"[RunPilot] Loaded config for run '{cfg.name}' "
        f"with image '{cfg.image}' and entrypoint '{cfg.entrypoint}'"
    )

    run_dir = create_run_dir(cfg.name)
    print(f"[RunPilot] Created run directory at: {run_dir}")

    # Initial metadata
    write_run_metadata(run_dir, cfg, status="pending")

    # Call the runner (Docker if available, stub otherwise)
    exit_code = run_local_container(cfg, run_dir)

    # Update metadata based on exit code
    final_status = "finished" if exit_code == 0 else "failed"
    write_run_metadata(run_dir, cfg, status=final_status, exit_code=exit_code)

    print(f"[RunPilot] Run completed with exit code {exit_code}")
    print(f"[RunPilot] Metadata written to {run_dir / 'run.json'}")


def _handle_list_command() -> None:
    # Proper implementation will read ~/.runpilot/runs and list them.
    print("[RunPilot] Listing runs is not implemented yet.")


if __name__ == "__main__":
    main()
