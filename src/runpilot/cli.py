from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .runner import run_local_container
from .storage import (
    create_run_dir,
    write_run_metadata,
    load_all_runs,
    load_run,
)
from .config import load_config
from .runner import run_local_container
from .storage import (
    create_run_dir,
    write_run_metadata,
    load_all_runs,
    load_run,
)
from .metrics import parse_metrics_from_log, write_metrics


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

    # list subcommand
    subparsers.add_parser(
        "list",
        help="List recorded runs",
    )

    # show subcommand
    show_parser = subparsers.add_parser(
        "show",
        help="Show details for a specific run",
    )
    show_parser.add_argument(
        "run_id",
        type=str,
        help="Run id to inspect",
    )

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "run":
        _handle_run_command(Path(args.config_path))
    elif args.command == "list":
        _handle_list_command()
    elif args.command == "show":
        _handle_show_command(args.run_id)
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
    
    # Extract metrics from logs if present
    log_path = run_dir / "logs.txt"
    metrics = parse_metrics_from_log(log_path)
    if metrics:
        write_metrics(run_dir, metrics)
        print(f"[RunPilot] Metrics written to {run_dir / 'metrics.json'}")

    print(f"[RunPilot] Run completed with exit code {exit_code}")
    print(f"[RunPilot] Metadata written to {run_dir / 'run.json'}")


def _handle_list_command() -> None:
    runs = load_all_runs()

    if not runs:
        print("[RunPilot] No runs found.")
        return

    # Simple table: ID (shortened), STATUS, CREATED_AT, EXIT_CODE
    header = f"{'ID':<32} {'STATUS':<10} {'EXIT':<5} {'CREATED_AT'}"
    print(header)
    print("-" * len(header))

    for r in runs:
        run_id = str(r.get("id", ""))[:32]
        status = str(r.get("status", ""))
        exit_code = r.get("exit_code")
        created_at = str(r.get("created_at", ""))
        exit_str = "" if exit_code is None else str(exit_code)
        print(f"{run_id:<32} {status:<10} {exit_str:<5} {created_at}")


def _handle_show_command(run_id: str) -> None:
    try:
        meta = load_run(run_id)
    except FileNotFoundError as exc:
        print(f"[RunPilot] {exc}")
        return
    except ValueError as exc:
        print(f"[RunPilot] Failed to load run metadata: {exc}")
        return

    print(f"Run ID      : {meta.get('id')}")
    print(f"Name        : {meta.get('name')}")
    print(f"Status      : {meta.get('status')}")
    print(f"Exit code   : {meta.get('exit_code')}")
    print(f"Created at  : {meta.get('created_at')}")
    print(f"Finished at : {meta.get('finished_at')}")
    print(f"Image       : {meta.get('image')}")
    print(f"Entrypoint  : {meta.get('entrypoint')}")
    print(f"Run dir     : {meta.get('run_dir')}")

    log_path = Path(str(meta.get("run_dir", ""))) / "logs.txt"
    print(f"Logs path   : {log_path}")
