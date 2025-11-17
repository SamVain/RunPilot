from __future__ import annotations

import os
import shutil
from pathlib import Path

from runpilot.archive import export_run, import_run
from runpilot.paths import get_run_dir


def test_export_import_roundtrip(tmp_path: Path, monkeypatch) -> None:
    # Isolate RUNPILOT_HOME under tmp_path
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("RUNPILOT_HOME", str(home))

    run_id = "test-run"
    run_dir = get_run_dir(run_id)
    run_dir.mkdir(parents=True)

    # Create minimal run files
    (run_dir / "run.json").write_text("{}", encoding="utf-8")
    (run_dir / "logs.txt").write_text("hello\n", encoding="utf-8")

    # Export
    archive_path = tmp_path / "exported.tar.gz"
    export_run(run_id, output_path=archive_path)
    assert archive_path.exists()

    # Remove original run directory
    shutil.rmtree(run_dir)
    assert not run_dir.exists()

    # Import
    imported_run_id = import_run(archive_path)
    assert imported_run_id == run_id

    restored_dir = get_run_dir(run_id)
    assert restored_dir.exists()
    assert (restored_dir / "run.json").exists()
    assert (restored_dir / "logs.txt").exists()
