from __future__ import annotations

from typing import Any, Dict
from .cloud_config import CloudConfig, save_cloud_config

import httpx


def login_via_api(
    api_base_url: str,
    email: str,
    password: str,
    default_project: str | None = None,
) -> CloudConfig:
    base = api_base_url.rstrip("/")
    url = f"{base}/v1/auth/login"

    resp = httpx.post(
        url,
        json={"email": email, "password": password},
        timeout=10.0,
    )
    resp.raise_for_status()
    body = resp.json()

    # OLD:
    # token = body.get("access_token")

    # NEW:
    token = body.get("token")
    if not token:
        raise RuntimeError("Cloud login response did not contain token")

    cfg = CloudConfig(
        api_base_url=api_base_url,
        token=token,
        default_project=default_project,
    )
    config_path = save_cloud_config(cfg)
    setattr(cfg, "config_path", config_path)
    return cfg



def _auth_headers(cfg: CloudConfig) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if cfg.token:
        headers["Authorization"] = f"Bearer {cfg.token}"
    return headers


def create_remote_run(cfg: CloudConfig, payload: Dict[str, Any]) -> str:
    """
    Create a run in RunPilot Cloud.

    Returns:
      cloud_run_id string from the API.
    """
    base = cfg.api_base_url.rstrip("/")
    url = f"{base}/v1/runs"

    resp = httpx.post(
        url,
        headers=_auth_headers(cfg),
        json=payload,
        timeout=10.0,
    )
    resp.raise_for_status()
    body = resp.json()
    cloud_run_id = body.get("cloud_run_id")
    if not cloud_run_id:
        raise RuntimeError("Cloud response did not contain cloud_run_id")
    return cloud_run_id


def upload_run_metrics(
    cfg: CloudConfig,
    cloud_run_id: str,
    payload: Dict[str, Any],
) -> None:
    """
    Upload metrics for an existing run in RunPilot Cloud.
    """
    base = cfg.api_base_url.rstrip("/")
    url = f"{base}/v1/runs/{cloud_run_id}/metrics"

    resp = httpx.put(
        url,
        headers=_auth_headers(cfg),
        json=payload,
        timeout=10.0,
    )
    resp.raise_for_status()
