# TODO: Implement retry logic with exponential backoff for all API calls
# TODO: Add request/response logging for debugging (when --verbose is enabled)
# TODO: Implement connection pooling for better performance
# TODO: Add support for API versioning (v1, v2, etc.)
# TODO: Implement webhook registration for real-time job status updates
# TODO: Add support for API rate limiting and quota management
# TODO: Implement client-side caching for frequently accessed data
# TODO: Add support for runpilot-cloud subscription tier validation
# TODO: Implement file chunking for large artifact uploads (>100MB)
# TODO: Add telemetry/analytics for usage tracking (opt-in)

import requests
import os
from typing import Optional, Dict, Any, List
from rich.console import Console
from .cloud_config import CloudConfig, save_cloud_config
import tarfile
import io
import secrets

console = Console()

# --- Internal Helpers ---

def _get_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

# --- Auth ---

def login_via_api(
    api_base_url: str, 
    email: str, 
    password: str, 
    default_project: Optional[str] = None
) -> CloudConfig:
    """Exchanges credentials for a token and saves config."""
    
    token_url = f"{api_base_url}/v1/auth/login"
    
    # FIX 1: Send JSON, strictly matching the LoginRequest model
    payload = {
        "email": email, 
        "password": password
    }
    
    try:
        resp = requests.post(token_url, json=payload)
        
        if resp.status_code == 422:
            console.print(f"[red]Server rejected payload:[/red] {resp.text}")
            raise ValueError("Login failed: Server could not parse the request.")
            
        resp.raise_for_status()
        
        data = resp.json()
        
        # FIX 2: Read the custom 'token' field, not 'access_token'
        if "token" not in data:
            raise KeyError(f"Server response missing 'token'. Got: {data.keys()}")
            
        token = data["token"]

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise ValueError("Login failed: Invalid email or password.")
        raise ConnectionError(f"Login failed: {e}")

    cfg = CloudConfig(
        api_base_url=api_base_url,
        token=token,
        default_project=default_project
    )
    save_cloud_config(cfg)
    return cfg

def get_identity(cfg: CloudConfig) -> Dict[str, Any]:
    url = f"{cfg.api_base_url}/v1/auth/me"
    resp = requests.get(url, headers=_get_headers(cfg.token))
    resp.raise_for_status()
    return resp.json()

# --- Projects ---

def list_projects(cfg: CloudConfig) -> List[Dict[str, Any]]:
    url = f"{cfg.api_base_url}/v1/projects"
    resp = requests.get(url, headers=_get_headers(cfg.token))
    resp.raise_for_status()
    return resp.json()

# --- Runs ---

def create_remote_run(cfg: CloudConfig, payload: Dict[str, Any]) -> str:
    url = f"{cfg.api_base_url}/v1/runs"
    try:
        resp = requests.post(url, json=payload, headers=_get_headers(cfg.token))
        resp.raise_for_status()
        data = resp.json()
        return data["cloud_run_id"]
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            console.print(f"[red]Validation Error:[/red] {e.response.text}")
            raise ValueError("Server rejected run data.")
        raise e

def upload_run_metrics(cfg: CloudConfig, cloud_run_id: str, metrics_payload: Dict[str, Any]):
    url = f"{cfg.api_base_url}/v1/runs/{cloud_run_id}/metrics"
    resp = requests.put(url, json=metrics_payload, headers=_get_headers(cfg.token))
    resp.raise_for_status()

def list_remote_runs(cfg: CloudConfig) -> List[Dict[str, Any]]:
    url = f"{cfg.api_base_url}/v1/runs/"
    resp = requests.get(url, headers=_get_headers(cfg.token))
    resp.raise_for_status()
    return resp.json()

def submit_job(cfg: CloudConfig, project_id: str, run_config: Dict[str, Any], source_dir: str, env_vars: Dict[str, str] = None) -> str:
    """
    Bundles current directory, creates a 'queued' run with secrets, and uploads code.
    """
    # TODO: Add .runpilotignore file support for excluding files from bundle
    # TODO: Implement incremental uploads (only changed files)
    # TODO: Add bundle size limits based on runpilot-cloud subscription tier
    # TODO: Support Git-based code fetching as alternative to bundling
    # TODO: Add progress bar for large file uploads
    # TODO: Implement client-side encryption for sensitive code
    console.print(f"[bold blue]RunPilot Cloud[/bold blue]: Preparing remote submission...")
    url = f"{cfg.api_base_url}/v1/runs"
    
    # 1. Create the Run Record (Status: Queued)
    run_id = f"remote_{secrets.token_hex(6)}"
    
    payload = {
        "run_id": run_id,
        "project_id": project_id,
        "status": "queued",
        "config": run_config,
        "tags": ["remote", "cli-submit"],
        # --- NEW: Send Secrets ---
        "env_vars": env_vars or {}
        # -------------------------
    }
    
    # --- STEP 1: REGISTER RUN ---
    try:
        resp = requests.post(url, json=payload, headers=_get_headers(cfg.token))
        if resp.status_code == 422:
             console.print(f"[red]Server Validation Error:[/red] {resp.text}")
             raise ValueError("Invalid payload")
        resp.raise_for_status()
        
        data = resp.json()
        cloud_id = data["cloud_run_id"]
        
    except Exception as e:
        raise ConnectionError(f"Failed to create remote job: {e}")

    # --- STEP 2: BUNDLE CODE ---
    console.print("[blue]📦 Bundling source code...[/blue]")
    bundle_path = "runpilot_bundle.tar.gz"
    
    def filter_tar(tarinfo):
        if "__pycache__" in tarinfo.name or ".git" in tarinfo.name or ".venv" in tarinfo.name:
            return None
        if tarinfo.name.endswith(".pyc"):
            return None
        return tarinfo

    with tarfile.open(bundle_path, "w:gz") as tar:
        tar.add(source_dir, arcname=".", filter=filter_tar)
    
    size_kb = os.path.getsize(bundle_path) / 1024
    console.print(f"[green]✔ Code bundled ({size_kb:.1f} KB)[/green]")
    
    # --- STEP 3: UPLOAD ARTIFACT (S3 Flow) ---
    console.print(f"[blue]⬆ Requesting upload URL...[/blue]")
    
    api_url = f"{cfg.api_base_url}/v1/runs/{cloud_id}/artifacts/code/upload-url"
    try:
        resp = requests.post(api_url, headers={"Authorization": f"Bearer {cfg.token}"})
        resp.raise_for_status()
        upload_info = resp.json()
        s3_url = upload_info["url"]
    except Exception as e:
        console.print(f"[red]Failed to get upload URL:[/red] {e}")
        return cloud_id 

    console.print(f"[blue]⬆ Uploading to S3...[/blue]")
    try:
        with open(bundle_path, "rb") as f:
            # Explicit Content-Type for S3 Signature
            upload_resp = requests.put(
                s3_url, 
                data=f, 
                headers={"Content-Type": "application/octet-stream"}
            )
            upload_resp.raise_for_status()
            console.print(f"[green]✔ Code uploaded successfully.[/green]")
    except Exception as e:
        console.print(f"[red]S3 Upload failed:[/red] {e}")
    
    return cloud_id

def update_remote_run_status(cfg: CloudConfig, cloud_run_id: str, status: str):
    """
    Reports the final status of a job back to the Cloud.
    """
    # TODO (DAY 2): Call instance shutdown endpoint after status update
    # TODO (DAY 2): Add instance_id parameter for EC2 cleanup
    url = f"{cfg.api_base_url}/v1/runs/{cloud_run_id}"
    
    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat()
    
    payload = {
        "status": status,
        "ended_at": now_iso
    }
    
    try:
        resp = requests.patch(url, json=payload, headers=_get_headers(cfg.token))
        resp.raise_for_status()
    except Exception as e:
        console.print(f"[red]Failed to report status:[/red] {e}")

def upload_run_logs(cfg: CloudConfig, cloud_run_id: str, log_path: str):
    """
    Uploads the local logs.txt to the Cloud.
    """
    url = f"{cfg.api_base_url}/v1/runs/{cloud_run_id}/logs"
    
    try:
        with open(log_path, "rb") as f:
            files = {"file": ("logs.txt", f, "text/plain")}
            resp = requests.post(url, files=files, headers={"Authorization": f"Bearer {cfg.token}"})
            resp.raise_for_status()
    except Exception as e:
        console.print(f"[red]Log upload failed:[/red] {e}")
        
def upload_run_logs(cfg: CloudConfig, cloud_run_id: str, log_path: str):
    """
    Uploads the local logs.txt to the Cloud.
    """
    url = f"{cfg.api_base_url}/v1/runs/{cloud_run_id}/logs"
    
    try:
        with open(log_path, "rb") as f:
            files = {"file": ("logs.txt", f, "text/plain")}
            resp = requests.post(url, files=files, headers={"Authorization": f"Bearer {cfg.token}"})
            resp.raise_for_status()
            console.print("[green]   ✔ Logs uploaded.[/green]")
    except Exception as e:
        console.print(f"[red]Log upload failed:[/red] {e}")