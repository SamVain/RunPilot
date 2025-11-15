# Day 1 – RunPilot

## What happened today

- Moved the project into WSL home (`~/RunPilot`) for better performance
- Created a Python virtual environment and installed RunPilot in editable mode
- Implemented:
  - `pyproject.toml` with CLI entry point
  - `runpilot` CLI scaffold using argparse
  - `config.py` with a minimal RunConfig dataclass and YAML loader
- Verified:
  - `runpilot` shows help
  - `runpilot run example.yaml` loads the config and prints stub output
- Cleaned up `.gitignore` to exclude venv, egg-info, pycache and example files

## Current status

- CLI and config loading are working end-to-end (stub only)
- No storage, Docker integration, metrics or DB yet
- Documentation and planning are in place for v0.1

## Focus for Day 2

- Implement a storage layer for run directories under `~/.runpilot/runs`
- Add a stubbed `runner.py` interface and wire it into the CLI
- Optionally add the first test for `load_config` using pytest
