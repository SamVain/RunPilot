from __future__ import annotations

import argparse
import json
import getpass

from .cloud_client import (
    login_via_api,
    create_remote_run,
    upload_run_metrics,
    list_remote_runs,
    get_identity,
)
from pathlib import Path
from .config import load_config, resolve_config_path
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
from .cloud_config import CloudConfig, load_cloud_config, save_cloud_config
from .paths import get_run_dir


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

    # login subcommand
    login_parser = subparsers.add_parser(
        "login",
        help="Configure RunPilot Cloud credentials",
    )

    login_parser.add_argument(
        "--api-base-url",
        help="Base URL for the RunPilot Cloud API (for example: https://api.runpilot.dev)",
    )
    login_parser.add_argument(
        "--email",
        help="Account email for RunPilot Cloud (used with password to obtain a token)",
    )
    login_parser.add_argument(
        "--token",
        help="API token for RunPilot Cloud (advanced: overrides email/password flow)",
    )
    login_parser.add_argument(
        "--project",
        help="Default project name or identifier",
    )

    # sync subcommand
    sync_parser = subparsers.add_parser(
        "sync",
        help="Sync a local run to RunPilot Cloud (skeleton, no real network calls yet)",
    )
    sync_parser.add_argument(
        "run_id",
        help="Run identifier to sync",
    )
    
    # whoami subcommand
    whoami_parser = subparsers.add_parser(
        "whoami",
        help="Show current RunPilot Cloud identity",
    )

    # list-remote subcommand
    list_remote_parser = subparsers.add_parser(
        "list-remote",
        help="List runs stored in RunPilot Cloud",
    )
    list_remote_parser.add_argument(
        "--json",
        action="store_true",
        help="Output remote runs as JSON instead of a table",
    )


    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        _handle_run_command(args.config_path)
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

    if args.command == "login":
        return _handle_login_command(
            api_base_url=getattr(args, "api_base_url", None),
            token=getattr(args, "token", None),
            default_project=getattr(args, "project", None),
        )

    if args.command == "sync":
        return _handle_sync_command(args.run_id)

    if args.command == "whoami":
        return _handle_whoami_command()

    if args.command == "list-remote":
        return _handle_list_remote_command(
            json_output=getattr(args, "json", False)
        )

    parser.error(f"Unknown command {args.command!r}")
    return 1


def _handle_run_command(config_ref: str) -> None:
    # Resolve either a direct path or a named run from runpilot.yaml
    config_path = resolve_config_path(config_ref)
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

def _handle_login_command(
    api_base_url: str | None,
    token: str | None,
    default_project: str | None,
) -> int:
    """
    Configure RunPilot Cloud credentials.

    For now this always uses username/password against the Cloud API
    to obtain an API token, then writes ~/.runpilot/cloud.yaml.
    """
    from . import cloud_client

    # Base URL prompt with default
    if not api_base_url:
        api_base_url = input(
            "RunPilot Cloud API base URL (default: http://127.0.0.1:8000): "
        ).strip()
        if not api_base_url:
            api_base_url = "http://127.0.0.1:8000"

    # Interactive email/password prompt
    email = input("RunPilot Cloud account email: ").strip()
    password = input("RunPilot Cloud password: ").strip()

    try:
        cfg = cloud_client.login_via_api(
            api_base_url=api_base_url,
            email=email,
            password=password,
            default_project=default_project,
        )
    except Exception as exc:
        print(f"[RunPilot] Cloud login failed: {exc}")
        return 1

    print(f"[RunPilot] Logged in as {email}")
    print(f"[RunPilot] Cloud configuration written to {cfg.config_path}")
    return 0


def _handle_sync_command(run_id: str) -> int:
    """
    Sync a local run to RunPilot Cloud.

    Behaviour:
      * Validates run directory exists.
      * Validates cloud configuration exists and has a token.
      * Reads run.json and metrics.json if present.
      * Creates a run in the Cloud and uploads metrics.
      * Logs what was done.
    """
    cfg = load_cloud_config()
    if cfg is None:
        print("[RunPilot] No cloud configuration found.")
        print("[RunPilot] Run `runpilot login` first to configure RunPilot Cloud.")
        return 1

    if not cfg.token:
        print("[RunPilot] Cloud configuration found but no token is set.")
        print("[RunPilot] Run `runpilot login` again to obtain a token.")
        return 1

    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        print(f"[RunPilot] Run directory not found for id: {run_id}")
        return 1

    run_json = run_dir / "run.json"
    metrics_json = run_dir / "metrics.json"
    logs_txt = run_dir / "logs.txt"
    outputs_dir = run_dir / "outputs"

    print(f"[RunPilot] Preparing to sync run {run_id} to RunPilot Cloud")
    print(f"[RunPilot] API base URL: {cfg.api_base_url}")
    if cfg.default_project:
        print(f"[RunPilot] Project: {cfg.default_project}")

    print("[RunPilot] Files:")
    print(f"  - run.json      : {'present' if run_json.exists() else 'missing'}")
    print(f"  - metrics.json  : {'present' if metrics_json.exists() else 'missing'}")
    print(f"  - logs.txt      : {'present' if logs_txt.exists() else 'missing'}")

    if outputs_dir.exists():
        artifacts = [p.relative_to(outputs_dir) for p in outputs_dir.rglob("*") if p.is_file()]
        print(f"  - outputs/      : {len(artifacts)} artifact(s)")
        for art in artifacts:
            print(f"      * {art}")
    else:
        print("  - outputs/      : none")

    if not run_json.exists():
        print("[RunPilot] Cannot sync: run.json is missing.")
        return 1

    # Load metadata
    try:
        meta = json.loads(run_json.read_text())
    except Exception as exc:
        print(f"[RunPilot] Failed to read run.json: {exc}")
        return 1

    # Build Cloud run payload
    cloud_run_payload: dict[str, Any] = {
        "run_id": meta.get("id", run_id),
        "project": cfg.default_project,
        "status": meta.get("status"),
        "started_at": meta.get("created_at"),
        "ended_at": meta.get("finished_at"),
        "params": meta.get("params") or {},
        "tags": meta.get("tags") or [],
        "config": {
            "name": meta.get("name"),
            "image": meta.get("image"),
            "entrypoint": meta.get("entrypoint"),
        },
    }

    try:
        cloud_run_id = create_remote_run(cfg, cloud_run_payload)
    except Exception as exc:
        print(f"[RunPilot] Failed to create run in Cloud: {exc}")
        return 1

    print(f"[RunPilot] Created remote run with id {cloud_run_id}")

    # Metrics (optional)
    if metrics_json.exists():
        try:
            metrics_data = json.loads(metrics_json.read_text())
        except Exception as exc:
            print(f"[RunPilot] Failed to read metrics.json: {exc}")
            metrics_data = {}

        # Be tolerant of schemas: either {summary, time_series} or plain summary
        if isinstance(metrics_data, dict):
            summary = metrics_data.get("summary", metrics_data)
            time_series = metrics_data.get("time_series", [])
        else:
            summary = {}
            time_series = []

        metrics_payload: dict[str, Any] = {
            "summary": summary or {},
            "time_series": time_series or [],
        }

        try:
            upload_run_metrics(cfg, cloud_run_id, metrics_payload)
            print("[RunPilot] Uploaded metrics to Cloud.")
        except Exception as exc:
            print(f"[RunPilot] Failed to upload metrics: {exc}")
    else:
        print("[RunPilot] No metrics.json found; skipping metrics upload.")

    print("[RunPilot] Sync complete (metadata + metrics).")
    # Logs and artifacts not yet uploaded
    return 0

def _handle_whoami_command() -> int:
    cfg = load_cloud_config()
    if cfg is None:
        print("[RunPilot] No cloud configuration found.")
        print("[RunPilot] Run `runpilot login` first to configure RunPilot Cloud.")
        return 1

    try:
        info = get_identity(cfg)
    except Exception as exc:
        print(f"[RunPilot] Failed to query identity from Cloud: {exc}")
        return 1

    user = info.get("user", {}) or {}
    org = info.get("org", {}) or {}

    print(f"[RunPilot] API base URL : {cfg.api_base_url}")
    print(f"[RunPilot] User        : {user.get('email')} (id={user.get('id')})")
    print(f"[RunPilot] Org         : {org.get('name')} (id={org.get('id')})")
    print(f"[RunPilot] Plan        : {org.get('plan_tier')}")
    return 0


def _handle_list_remote_command(json_output: bool = False) -> int:
    cfg = load_cloud_config()
    if cfg is None:
        print("[RunPilot] No cloud configuration found.")
        print("[RunPilot] Run `runpilot login` first to configure RunPilot Cloud.")
        return 1

    try:
        runs = list_remote_runs(cfg)
    except Exception as exc:
        print(f"[RunPilot] Failed to list remote runs: {exc}")
        return 1

    if json_output:
        print(json.dumps(runs, indent=2, sort_keys=True, default=str))
        return 0

    if not runs:
        print("[RunPilot] No remote runs found.")
        return 0

    header = f"{'CLOUD_ID':<16} {'RUN_ID':<32} {'STATUS':<10} {'PROJECT':<16} {'STARTED'}"
    print(header)
    print("-" * len(header))

    for r in runs:
        cloud_id = str(r.get("cloud_run_id", ""))[:16]
        run_id = str(r.get("run_id", ""))[:32]
        status = str(r.get("status", ""))
        project = str(r.get("project", ""))[:16]
        started_at = str(r.get("started_at", ""))
        print(f"{cloud_id:<16} {run_id:<32} {status:<10} {project:<16} {started_at}")

    return 0
