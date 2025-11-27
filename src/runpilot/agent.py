# src/runpilot/agent.py
import os
import tarfile
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from rich.console import Console

from .cloud_config import CloudConfig, load_cloud_config
from .cloud_client import update_remote_run_status
from .config import RunConfig
from .runner import run_local_container
from .storage import create_run_dir, write_run_metadata

console = Console()


def start_agent(poll_interval: int = 5, once: bool = False):
    """
    Main Agent Loop: Poll -> Claim -> Run -> Report.

    If once=True, process at most one job then exit.
    """
    cfg = load_cloud_config()
    if not cfg or not cfg.token:
        console.print("[red]Agent failed: Not logged in. Run 'runpilot login'.[/red]")
        return

    console.print("[bold green]🤖 RunPilot Agent Active[/bold green]")
    console.print(f"Target: {cfg.api_base_url}")
    console.print(f"Polling for 'queued' jobs every {poll_interval}s...")

    while True:
        try:
            job_processed = _cycle(cfg)
        except KeyboardInterrupt:
            console.print("\n[yellow]Agent stopping...[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Agent Error:[/red] {e}")
            job_processed = False

        if once and job_processed:
            break

        time.sleep(poll_interval)


def _cycle(cfg: CloudConfig) -> bool:
    """
    One scheduling cycle.

    Returns True if a job was claimed and processed, False otherwise.
    """
    from .cloud_client import (
        upload_run_logs,
        upload_run_metrics_file,
        upload_run_artifacts,
        request_instance_shutdown,
    )

    headers = {"Authorization": f"Bearer {cfg.token}"}

    # 1. Ask for work
    try:
        resp = requests.post(f"{cfg.api_base_url}/v1/runs/acquire", headers=headers)
        resp.raise_for_status()
        job = resp.json()
    except Exception:
        # No work or auth error etc
        return False

    if not job:
        return False

    # 2. Claimed
    cloud_id = job["cloud_run_id"]
    console.print(f"\n[bold blue]🚀 Claimed Job: {cloud_id}[/bold blue]")

    job_config = job.get("config", {}) or {}

    # Secrets passed from cloud
    secrets = job.get("env_vars", {}) or {}
    if secrets:
        console.print(f"   🔒 Secrets injected: {list(secrets.keys())}")

    # Build RunConfig for local execution
    run_cfg = RunConfig(
        name=job_config.get("name", "remote-job"),
        image=job.get("image") or job_config.get("image"),
        entrypoint=job.get("entrypoint") or job_config.get("entrypoint"),
        env_vars=secrets,
        use_gpu=bool(job_config.get("use_gpu", False)) or bool(job_config.get("gpu", False)),
    )

    console.print(f"   Task: {run_cfg.entrypoint}")
    console.print(f"   🧪 use_gpu from job: {run_cfg.use_gpu}")

    # 3. Prepare local workspace
    run_dir = create_run_dir(run_cfg.name)
    write_run_metadata(run_dir, run_cfg, status="running")

    # 4. DOWNLOAD & EXTRACT ARTIFACTS (code bundle from S3 or mock)
    console.print("   ⬇ Requesting download URL...")
    api_url = f"{cfg.api_base_url}/v1/runs/{cloud_id}/artifacts/code/download-url"

    try:
        resp = requests.get(api_url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        s3_url = data.get("url")

        if s3_url:
            # If it is a relative path (mock), join with api_base_url
            download_url = urljoin(cfg.api_base_url, s3_url)

            console.print("   ⬇ Downloading from S3...")
            r = requests.get(download_url)
            r.raise_for_status()

            bundle_path = run_dir / "source.tar.gz"
            with open(bundle_path, "wb") as f:
                f.write(r.content)

            with tarfile.open(bundle_path, "r:gz") as tar:
                tar.extractall(path=run_dir)
            console.print(f"   ✔ Code extracted to {run_dir}")
        else:
            console.print("   ⚠ No code bundle found (using image default).")

    except Exception as e:
        console.print(f"   [red]Artifact error:[/red] {e}")

    # 5. Execute
    exit_code = run_local_container(run_cfg, run_dir, working_dir=run_dir)

    status = "success" if exit_code == 0 else "failed"
    console.print(f"[bold]Job finished: {status} (Exit: {exit_code})[/bold]")

    # 6. Upload logs
    log_path = run_dir / "logs.txt"
    if log_path.exists():
        upload_run_logs(cfg, cloud_id, str(log_path))

    # 7. Upload metrics if present
    metrics_path = run_dir / "metrics.json"
    if metrics_path.exists():
        upload_run_metrics_file(cfg, cloud_id, str(metrics_path))

    # 8. Upload any artifacts directory
    artifacts_dir = run_dir / "artifacts"
    if artifacts_dir.exists() and artifacts_dir.is_dir():
        upload_run_artifacts(cfg, cloud_id, artifacts_dir)

    # 9. Report status back to cloud (will set ended_at on server side)
    update_remote_run_status(cfg, cloud_id, status)

    # 10. Request EC2 shutdown if running in EC2 mode
    if os.getenv("RUNPILOT_EC2_MODE", "").lower() in ("true", "1", "yes"):
        console.print("   📴 Requesting EC2 shutdown...")
        request_instance_shutdown(cfg, cloud_id)

    return True
