from __future__ import annotations
import subprocess
import shlex
import os
from pathlib import Path
from rich.console import Console
from .config import RunConfig

console = Console()

def run_local_container(cfg: RunConfig, run_dir: Path, working_dir: Path | None = None) -> int:
    """
    Runs the job. 
    - run_dir: Where logs/metrics go.
    - working_dir: Where the code execution happens (Defaults to os.getcwd() if None).
    """
    run_dir = Path(run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Default execution location: CWD (Local run) or run_dir (Remote Agent run)
    # CRITICAL: Docker requires absolute paths for volume mounts.
    if working_dir:
        exec_dir = Path(working_dir).resolve()
    else:
        exec_dir = Path(os.getcwd()).resolve()

    # 1. Check Docker
    docker_avail = _check_docker()
    
    if cfg.image and docker_avail:
        return _run_in_docker(cfg, run_dir, exec_dir)
    else:
        if cfg.image:
            console.print(f"[yellow]⚠ Docker not found. Falling back to local.[/yellow]")
        return _run_locally(cfg, run_dir, exec_dir)

def _check_docker() -> bool:
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        return True
    except Exception:
        return False

def _run_in_docker(cfg: RunConfig, run_dir: Path, exec_dir: Path) -> int:
    console.print(f"[blue]🐳 Starting Docker ({cfg.image})...[/blue]")
    log_path = run_dir / "logs.txt"
    
    try:
        cmd_args = shlex.split(cfg.entrypoint)
    except:
        cmd_args = cfg.entrypoint.split()

    # Docker command construction
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{str(exec_dir)}:/app",
        "-w", "/app"
    ]
    
    # --- INJECT SECRETS ---
    # We pass environment variables to the container here
    if cfg.env_vars:
        for key, val in cfg.env_vars.items():
            docker_cmd.extend(["-e", f"{key}={val}"])
    # ----------------------

    docker_cmd.append(cfg.image)
    docker_cmd.extend(cmd_args)

    with log_path.open("w", encoding="utf-8") as f:
        try:
            # We don't use check=True here because we want to capture the exit code manually
            proc = subprocess.run(docker_cmd, stdout=f, stderr=subprocess.STDOUT, text=True)
            
            if proc.returncode != 0:
                # If it fails, print the last few lines of the log to the console for debugging
                console.print(f"[red]Docker exited with code {proc.returncode}. Check logs.[/red]")
            
            return proc.returncode
        except Exception as e:
            console.print(f"[red]Docker execution error:[/red] {e}")
            f.write(f"\nDocker execution error: {e}\n")
            return 1

def _run_locally(cfg: RunConfig, run_dir: Path, exec_dir: Path) -> int:
    console.print("[blue]⚡ Starting Local Process...[/blue]")
    log_path = run_dir / "logs.txt"
    
    try:
        cmd_args = shlex.split(cfg.entrypoint)
    except:
        cmd_args = cfg.entrypoint.split()

    # Prepare environment variables for local process
    env = os.environ.copy()
    if cfg.env_vars:
        env.update(cfg.env_vars)

    with log_path.open("w", encoding="utf-8") as f:
        try:
            # IMPORTANT: Run inside the execution directory
            proc = subprocess.run(
                cmd_args, 
                stdout=f, 
                stderr=subprocess.STDOUT, 
                text=True, 
                check=False,
                cwd=str(exec_dir),
                env=env  # <--- Inject secrets
            )
            return proc.returncode
        except Exception as e:
            console.print(f"[red]Local error:[/red] {e}")
            f.write(f"\nLocal error: {e}\n")
            return 1