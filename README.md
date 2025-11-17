# RunPilot

RunPilot is a lightweight orchestration tool for running reproducible AI training jobs.

You define a training run using a simple YAML config. RunPilot then creates an isolated run directory, executes the run using a container engine (when available), captures logs, records metadata, and gives you a searchable history of previous runs.

This repository is the open-source core. \
The long-term plan is:

- free, open core CLI + local runner here

- paid RunPilot Cloud for remote execution, dashboards, teams, RBAC, SSO, audit, enterprise support

Status: Early v0.1 \
Runs execute locally. If Docker is missing, RunPilot gracefully falls back and still records a failed run with logs stored.

---

## Vision
RunPilot should become the easiest way to:

- Define a training run in a single config file
- Run that job locally in a container with reproducibility by default
- Capture logs and metrics automatically
- Keep a searchable history of runs for comparison and auditing
- Seamlessly scale the same workflow to cloud or cluster execution

In short: `Docker Compose` for machine learning training experiments.

## v0.1 Features (current)

This initial milestone includes:

- `runpilot run <config.yaml>`
- `runpilot list` (show run history)
- `runpilot show <run_id>` (view one run)
- YAML-based config validation
- Per-run directory under: `~/.runpilot/runs/<run_id>/`
- `run.json` metadata: timestamps, exit code, status, image, entrypoint
- `logs.txt` capturing all stdout/stderr
- Docker-based execution if available, fallback if not
- Tests for config, metadata, runner, metrics parsing (WIP)

Upcoming soon:
- Metrics extraction into metrics.json
- Improved CLI formatting / filters
- Optional SQLite backend (planned, not implemented)

---

## Quickstart (dev)

### 1. Clone the repo
```bash
git clone git@github.com:SamVain/RunPilot.git
cd RunPilot
```
### 2. Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install RunPilot in editable mode
```bash
python -m pip install --upgrade pip
python -m pip install -e .

```

### 4. Create a simple example config
```yaml
# example.yaml
name: hello-run
image: "python:3.11-slim"
entrypoint: "python -c 'print("hello from RunPilot stub")'"
```

### 5. Run it!
```bash
runpilot run example.yaml
```

Results will appear under:
`~/.runpilot/runs/<run_id>`

---

## Example (future)

This is the kind of experience v0.1 and beyond will aim for:

```bash
runpilot run config.yaml
```

With a config like:

```yaml
name: mnist-cnn-baseline
image: "pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime"
entrypoint: "python train.py"
env:
  EPOCHS: 10
  LR: 0.001
mounts:
  code: "./src"
  data: "./data"
resources:
  gpus: 1
  cpu: 4
  memory: "16g"
metrics:
  - "train_loss"
  - "val_accuracy"
```

---

## Project Status
RunPilot is currently in the early foundation stage.
The goals are to:

- Deliver a stable local runner
- Support metrics logging and search
- Refine the CLI and UX
- Prepare for future cloud execution model

---

## License
Planned: MIT or Apache 2.0 (to be finalised).