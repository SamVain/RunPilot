from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_config
from .runner import run_local_container
from .storage import (
    create_run_dir,
    write_run_metadata,
    load_all_runs,
    load_run,
)
from .metrics import parse_metrics_from_log, write_metrics
from .cli_metrics import metrics_command
from .archive import export_run, import_run, RunNotFoundError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="runpilot")
    subparsers = parser.add_subparsers(dest="command", required=True)

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
    list_parser = subparsers.add_parser(
        "list",
        help="List recorded runs",
    )
    list_parser.add_argument(
        "--json",
        action="store_true",
        help="Output runs as JSON instead of a table",
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
    show_parser.add_argument(
        "--json",
        action="store_true",
        help="Output run metadata as JSON instead of a table",
    )

    # metrics subcommand
    metrics_parser = subparsers.add_parser(
        "metrics",
        help="Show metrics for a run",
    )
    metrics_parser.add_argument(
        "run_id",
        help="Run identifier",
    )
    metrics_parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw metrics.json as JSON",
    )

    # export subcommand
    export_parser = subparsers.add_parser(
        "export",
        help="Export a run to a tar.gz archive",
    )
    export_parser.add_argument(
        "run_id",
        help="Run identifier to export",
    )
    export_parser.add_argument(
        "--output",
        "-o",
        help="Output archive path (default: <run-id>.tar.gz in current directory)",
    )

    # import subcommand
    import_parser = subparsers.add_parser(
        "import",
        help="Import a run from a tar.gz archive",
    )
    import_parser.add_argument(
        "archive_path",
        help="Path to an exported run archive (tar.gz)",
    )
    import_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing run directory if it already exists",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        _handle_run_command(Path(args.config_path))
        return 0

    if args.command == "list":
        _handle_list_command(json_output=getattr(args, "json", False))
        return 0

    if args.command == "show":
        _handle_show_command(args.run_id, json_output=getattr(args, "json", False))
        return 0

    if args.command == "metrics":
        return metrics_command(run_id=args.run_id, json_output=args.json)

    if args.command == "export":
        return _handle_export_command(args.run_id, args.output)

    if args.command == "import":
        return _handle_import_command(Path(args.archive_path), overwrite=args.force)

    parser.error(f"Unknown command {args.command!r}")
    return 1


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
    parsed_metrics = parse_metrics_from_log(log_path)

    # Build metrics summary (scalar values only)
    summary: dict[str, float] = {}

    final_metrics = parsed_metrics.get("final") if isinstance(parsed_metrics, dict) else None
    if isinstance(final_metrics, dict):
        for key, value in final_metrics.items():
            try:
                summary[key] = float(value)
            except (TypeError, ValueError):
                continue

    # Always include exit code as a metric
    try:
        summary["exit_code"] = float(exit_code)
    except (TypeError, ValueError):
        pass

    if summary:
        run_id = run_dir.name
        write_metrics(run_dir=run_dir, run_id=run_id, summary=summary)
        print(f"[RunPilot] Metrics written to {run_dir / 'metrics.json'}")

    print(f"[RunPilot] Run completed with exit code {exit_code}")
    print(f"[RunPilot] Metadata written to {run_dir / 'run.json'}")


def _handle_list_command(json_output: bool = False) -> None:
    runs = load_all_runs()

    if json_output:
        print(json.dumps(runs, indent=2, sort_keys=True, default=str))
        return

    if not runs:
        print("[RunPilot] No runs found.")
        return

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


def _handle_show_command(run_id: str, json_output: bool = False) -> None:
    try:
        meta = load_run(run_id)
    except FileNotFoundError as exc:
        print(f"[RunPilot] {exc}")
        return
    except ValueError as exc:
        print(f"[RunPilot] Failed to load run metadata: {exc}")
        return

    if json_output:
        print(json.dumps(meta, indent=2, sort_keys=True, default=str))
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


def _handle_export_command(run_id: str, output_arg: str | None) -> int:
    from pathlib import Path as _Path

    output_path = _Path(output_arg) if output_arg else None

    try:
        archive_path = export_run(run_id, output_path=output_path)
    except RunNotFoundError as exc:
        print(f"[RunPilot] {exc}")
        return 1

    print(f"[RunPilot] Exported run {run_id} to {archive_path}")
    return 0


def _handle_import_command(archive_path: Path, overwrite: bool = False) -> int:
    try:
        run_id = import_run(archive_path, overwrite=overwrite)
    except FileNotFoundError as exc:
        print(f"[RunPilot] {exc}")
        return 1
    except FileExistsError as exc:
        print(f"[RunPilot] {exc}")
        return 1
    except ValueError as exc:
        print(f"[RunPilot] Failed to import archive: {exc}")
        return 1

    print(f"[RunPilot] Imported run {run_id} from {archive_path}")
    return 0
