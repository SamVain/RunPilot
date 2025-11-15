from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class RunConfig:
    """Minimal representation of a RunPilot config."""

    name: str
    image: str
    entrypoint: str


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
    )
