from pathlib import Path
from textwrap import dedent

import pytest

from runpilot.config import load_config
from runpilot.config import RunConfig
from runpilot.storage import (
    create_run_dir,
    write_run_metadata,
    load_run,
    load_all_runs,
)


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

def test_write_and_load_metadata(monkeypatch, tmp_path: Path) -> None:
    # Force RunPilot to use a temp HOME
    monkeypatch.setenv("HOME", str(tmp_path))

    cfg = RunConfig(
        name="test-run",
        image="python:3.11-slim",
        entrypoint="echo hi",
    )

    run_dir = create_run_dir(cfg.name)
    # Simulate a completed run
    write_run_metadata(run_dir, cfg, status="pending")
    write_run_metadata(run_dir, cfg, status="finished", exit_code=0)

    meta = load_run(run_dir.name)

    assert meta["id"] == run_dir.name
    assert meta["run_dir"] == str(run_dir)
    assert meta["name"] == "test-run"
    assert meta["image"] == "python:3.11-slim"
    assert meta["entrypoint"] == "echo hi"
    assert meta["status"] == "finished"
    assert meta["exit_code"] == 0
    assert "created_at" in meta
    assert "finished_at" in meta

    all_runs = load_all_runs()
    assert len(all_runs) == 1
    assert all_runs[0]["id"] == run_dir.name


def test_load_run_missing_raises(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))

    # No runs created
    try:
        load_run("does-not-exist")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError for missing run")