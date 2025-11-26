from __future__ import annotations

# TODO: Add schema validation with detailed error messages (consider pydantic)
# TODO: Support YAML anchors and aliases for config reuse
# TODO: Add environment variable interpolation (${VAR_NAME})
# TODO: Support config inheritance (base config + overrides)
# TODO: Add validation for Docker image name format
# TODO: Support multiple entrypoints for multi-stage jobs
# TODO: Add support for resource limits (memory, CPU, GPU count)
# TODO: Implement config versioning for backwards compatibility
# TODO: Add support for secrets reference (e.g., ${{ secrets.API_KEY }})
# TODO: Support conditional configuration based on target environment

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclass
class RunConfig:
    """Minimal representation of a RunPilot config."""
    # TODO: Add timeout field for job execution limits
    # TODO: Add retry_count field for automatic job retries
    # TODO: Add depends_on field for job dependencies
    # TODO: Add artifacts field for output file patterns
    # TODO: Add resource_class field for tier-based compute selection

    name: str
    image: str
    entrypoint: str
    env_vars: Dict[str, str] = field(default_factory=dict)
    # --- NEW FIELD ---
    use_gpu: bool = False
    # -----------------


def load_config(path: str | Path) -> RunConfig:
    """
    Load a RunPilot config from a YAML file and perform basic validation.
    """
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data: Any = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Config file {path} must contain a YAML mapping at the top level.")

    required_keys = ("name", "image", "entrypoint")
    missing = [key for key in required_keys if key not in data]

    if missing:
        missing_str = ", ".join(missing)
        raise ValueError(f"Config file {path} is missing required keys: {missing_str}")

    return RunConfig(
        name=str(data["name"]),
        image=str(data["image"]),
        entrypoint=str(data["entrypoint"]),
        # --- READ GPU FLAG ---
        use_gpu=bool(data.get("gpu", False))
        # ---------------------
    )

def resolve_config_path(ref: str, cwd: Optional[Path] = None) -> Path:
    """
    Resolve a config reference to a concrete file path.
    """
    if cwd is None:
        cwd = Path.cwd()
    else:
        cwd = Path(cwd)

    # 1. direct file path
    p = Path(ref)
    if not p.is_absolute():
        p = cwd / p
    if p.exists():
        return p

    # 2. project-level config: runpilot.yaml
    project_config = cwd / "runpilot.yaml"
    if project_config.exists():
        import yaml

        data = yaml.safe_load(project_config.read_text(encoding="utf-8")) or {}
        runs: Dict[str, Any] = data.get("runs") or {}
        if ref in runs:
            run_def = runs[ref]
            if isinstance(run_def, dict) and "config" in run_def:
                cfg_path = cwd / str(run_def["config"])
                if cfg_path.exists():
                    return cfg_path
                raise FileNotFoundError(
                    f"Config file for run '{ref}' not found at {cfg_path}"
                )

    raise FileNotFoundError(f"Config file not found or run alias not defined: {ref}")