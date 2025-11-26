# TODO: Add support for project templates with pre-configured settings
# TODO: Implement project-level default configurations
# TODO: Add support for project team members and permissions (Pro feature)
# TODO: Implement project activity feed and audit log
# TODO: Add support for project webhooks for CI/CD integration
# TODO: Implement project quotas and usage limits based on runpilot-cloud tier
# TODO: Add support for project environments (dev, staging, prod)
# TODO: Implement project billing integration with runpilot-cloud
# TODO: Add support for project-level secrets management
# TODO: Implement project cloning/forking functionality

from dataclasses import dataclass
from typing import Optional
import yaml
from pathlib import Path

PROJECT_CONFIG_FILE = ".runpilot/project.yaml"


@dataclass
class LocalProjectBinding:
    # TODO: Add environment field (dev, staging, prod)
    # TODO: Add default_image field for project-wide image defaults
    # TODO: Add default_gpu field for GPU preferences
    project_id: int
    project_name: str
    api_base_url: str

def load_local_project_binding() -> Optional[LocalProjectBinding]:
    """Reads .runpilot/project.yaml from the current directory."""
    path = Path(PROJECT_CONFIG_FILE)
    if not path.exists():
        return None
    
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            # Basic validation
            if not data or "project_id" not in data:
                return None
                
            return LocalProjectBinding(
                project_id=data.get("project_id"),
                project_name=data.get("project_name"),
                api_base_url=data.get("api_base_url", "")
            )
    except Exception:
        return None

def save_local_project_binding(binding: LocalProjectBinding) -> Path:
    """Writes the project binding to disk."""
    path = Path(PROJECT_CONFIG_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "project_id": binding.project_id,
        "project_name": binding.project_name,
        "api_base_url": binding.api_base_url
    }
    
    with open(path, "w") as f:
        yaml.dump(data, f)
    
    return path