import time
import requests
import tarfile
import os
from rich.console import Console
from .cloud_config import load_cloud_config, CloudConfig
from .cloud_client import update_remote_run_status
from .runner import run_local_container
from .config import RunConfig
from .storage import create_run_dir, write_run_metadata

console = Console()

def start_agent(poll_interval: int = 5):
    """
    Main Agent Loop: Poll -> Claim -> Run -> Report.
    """
    cfg = load_cloud_config()
    if not cfg or not cfg.token:
        console.print("[red]Agent failed: Not logged in. Run 'runpilot login'.[/red]")
        return

    console.print(f"[bold green]🤖 RunPilot Agent Active[/bold green]")
    console.print(f"Target: {cfg.api_base_url}")
    console.print(f"Polling for 'queued' jobs every {poll_interval}s...")

    while True:
        try:
            _cycle(cfg)
        except KeyboardInterrupt:
            console.print("\n[yellow]Agent stopping...[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Agent Error:[/red] {e}")

        time.sleep(poll_interval)

def _cycle(cfg: CloudConfig):
    headers = {"Authorization": f"Bearer {cfg.token}"}

    # 1. Ask for work
    try:
        resp = requests.post(f"{cfg.api_base_url}/v1/runs/acquire", headers=headers)
        resp.raise_for_status()
        job = resp.json()
    except Exception:
        return

    if not job:
        return

    # 2. Claimed!
    cloud_id = job['cloud_run_id']
    console.print(f"\n[bold blue]🚀 Claimed Job: {cloud_id}[/bold blue]")

    job_config = job.get('config', {})
    
    # --- EXTRACT SECRETS ---
    secrets = job.get('env_vars', {})
    if secrets:
        # Print keys only for security
        console.print(f"   🔒 Secrets injected: {list(secrets.keys())}")
    # -----------------------

    run_cfg = RunConfig(
        name=job_config.get('name', 'remote-job'),
        image=job.get('image') or job_config.get('image'),
        entrypoint=job.get('entrypoint') or job_config.get('entrypoint'),
        env_vars=secrets  # <--- POPULATE CONFIG
    )

    console.print(f"   Task: {run_cfg.entrypoint}")

    # 3. Prepare Local Workspace (Sandbox)
    run_dir = create_run_dir(run_cfg.name)
    write_run_metadata(run_dir, run_cfg, status="running")

    # 4. DOWNLOAD & EXTRACT ARTIFACTS (S3 Flow)
    console.print(f"   ⬇ Requesting download URL...")
    api_url = f"{cfg.api_base_url}/v1/runs/{cloud_id}/artifacts/code/download-url"

    try:
        # 1. Get Presigned URL
        resp = requests.get(api_url, headers=headers)

        if resp.status_code == 200:
            s3_url = resp.json()["url"]

            # 2. Download from S3
            console.print(f"   ⬇ Downloading from S3...")
            
            r = requests.get(s3_url)
            
            if r.status_code == 200:
                bundle_path = run_dir / "source.tar.gz"
                with open(bundle_path, 'wb') as f:
                    f.write(r.content)

                with tarfile.open(bundle_path, "r:gz") as tar:
                    tar.extractall(path=run_dir)
                console.print(f"   ✔ Code extracted to {run_dir}")
            else:
                console.print(f"   ⚠ S3 Download failed: {r.status_code}")
                console.print(f"   ❌ S3 Response: {r.text}")
        else:
            console.print(f"   ⚠ No code bundle found (using image default).")

    except Exception as e:
         console.print(f"   [red]Artifact error:[/red] {e}")

    # 5. EXECUTE
    exit_code = run_local_container(run_cfg, run_dir, working_dir=run_dir)

    status = "success" if exit_code == 0 else "failed"
    console.print(f"[bold]Job finished: {status} (Exit: {exit_code})[/bold]")

    # 6. UPLOAD LOGS
    log_path = run_dir / "logs.txt"
    if log_path.exists():
        from .cloud_client import upload_run_logs
        upload_run_logs(cfg, cloud_id, str(log_path))

    # 7. Report Status
    update_remote_run_status(cfg, cloud_id, status)