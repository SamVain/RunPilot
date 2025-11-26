from __future__ import annotations

# TODO: Add support for multiple cloud profiles (work, personal, etc.)
# TODO: Implement config encryption for sensitive tokens
# TODO: Add support for environment variable overrides
# TODO: Implement config migration for schema changes
# TODO: Add support for organization-level config sharing
# TODO: Implement config validation on load
# TODO: Add support for config file permissions checking
# TODO: Implement config sync with runpilot-cloud for team settings
# TODO: Add support for config expiry warnings (token expiration)
# TODO: Implement config backup and restore functionality

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional

from .paths import get_base_dir

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


CONFIG_FILENAME = "cloud.yaml"


@dataclass
class CloudConfig:
    # TODO: Add refresh_token field for token renewal
    # TODO: Add expires_at field for token expiration tracking
    # TODO: Add organization_id field for org context
    # TODO: Add region field for API endpoint selection
    api_base_url: str
    token: str
    default_project: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def get_cloud_config_path() -> Path:
    """
    Return the path to the cloud config file, usually:
      ~/.runpilot/cloud.yaml
    """
    return get_base_dir() / CONFIG_FILENAME


def load_cloud_config() -> Optional[CloudConfig]:
    """
    Load cloud configuration if present, otherwise return None.
    """
    path = get_cloud_config_path()
    if not path.exists():
        return None

    if yaml is None:
        raise RuntimeError("PyYAML is required for cloud config but is not installed")

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    api_base_url = data.get("api_base_url")
    token = data.get("token")
    default_project = data.get("default_project")

    if not api_base_url or not token:
        return None

    return CloudConfig(
        api_base_url=str(api_base_url),
        token=str(token),
        default_project=str(default_project) if default_project else None,
    )


def save_cloud_config(cfg: CloudConfig) -> Path:
    """
    Write cloud.yaml under the RunPilot base directory.
    """
    if yaml is None:
        raise RuntimeError("PyYAML is required for cloud config but is not installed")

    base_dir = get_base_dir()
    base_dir.mkdir(parents=True, exist_ok=True)

    path = get_cloud_config_path()
    payload = cfg.to_dict()

    path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")
    return path
