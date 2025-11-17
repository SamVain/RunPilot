from pathlib import Path

from runpilot.config import RunConfig
from runpilot import runner


def test_runner_fallback_when_docker_missing(tmp_path: Path, monkeypatch) -> None:
    # Force subprocess.run inside runpilot.runner to simulate missing docker
    def fake_run(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr("runpilot.runner.subprocess.run", fake_run)

    cfg = RunConfig(
        name="test-run",
        image="python:3.11-slim",
        entrypoint="echo hi",
    )

    run_dir = tmp_path / "run"
    run_dir.mkdir()

    exit_code = runner.run_local_container(cfg, run_dir)

    # Fallback path should set exit_code to 1 and write logs.txt
    assert exit_code == 1
    log_path = run_dir / "logs.txt"
    assert log_path.is_file()
    content = log_path.read_text(encoding="utf-8")
    assert "Docker is not installed" in content
