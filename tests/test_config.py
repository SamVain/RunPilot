from pathlib import Path
from textwrap import dedent

import pytest

from runpilot.config import load_config


def test_load_config_minimal(tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(
        dedent(
            """
            name: test-run
            image: python:3.11-slim
            entrypoint: "python -c 'print(\\\"hi\\\")'"
            """
        ),
        encoding="utf-8",
    )

    cfg = load_config(cfg_path)

    assert cfg.name == "test-run"
    assert cfg.image == "python:3.11-slim"
    assert "python -c" in cfg.entrypoint


def test_missing_required_keys_raises(tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError):
        load_config(cfg_path)
