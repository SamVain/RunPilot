from __future__ import annotations

from pathlib import Path

from runpilot.config import resolve_config_path


def test_resolve_direct_path(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("name: direct\nimage: test\nentrypoint: echo hi\n", encoding="utf-8")

    resolved = resolve_config_path(str(cfg), cwd=tmp_path)
    assert resolved == cfg


def test_resolve_named_run_from_runpilot_yaml(tmp_path: Path) -> None:
    cfg = tmp_path / "example.yaml"
    cfg.write_text("name: hello\nimage: test\nentrypoint: echo hi\n", encoding="utf-8")

    runpilot_yaml = tmp_path / "runpilot.yaml"
    runpilot_yaml.write_text(
        "runs:\n  hello:\n    config: example.yaml\n", encoding="utf-8"
    )

    resolved = resolve_config_path("hello", cwd=tmp_path)
    assert resolved == cfg
