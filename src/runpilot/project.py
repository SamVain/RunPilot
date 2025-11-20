from dataclasses import dataclass
from typing import Optional
import yaml
from pathlib import Path

PROJECT_CONFIG_FILE = ".runpilot/project.yaml"

@dataclass
class LocalProjectBinding:
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