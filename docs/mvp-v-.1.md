# RunPilot v0.1 MVP

## Goal

Deliver a minimal but usable CLI tool that can:

- Read a run configuration from a YAML file
- Use Docker or Podman to run a training job in a container
- Stream logs to the console
- Save logs and basic metadata per run
- Capture simple metrics from stdout
- Store run history in a lightweight local database

This version is focused entirely on **local execution**. No remote or cluster support yet.

---

## Core components

### 1. CLI

Binary name: `runpilot`

Initial commands:

- `runpilot run <config_path>`  
  Read a YAML config and execute a run.

- `runpilot list`  
  List previous runs with basic info.

- `runpilot show <run_id>`  
  Show details and paths for a specific run.

Optional for v0.1:

- `runpilot init`  
  Create a sample config in the current directory.

---

### 2. Config format

YAML file with the following minimal fields:

```yaml
name: mnist-cnn-baseline
image: "pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime"
entrypoint: "python train.py"
workdir: "/workspace"

env:
  EPOCHS: 10
  LR: 0.001

mounts:
  code: "./src"
  data: "./data"

resources:
  gpus: 1
  cpu: 4
  memory: "8g"

metrics:
  - "train_loss"
  - "val_accuracy"
```

v0.1 requirement: all top level sections are optional except name, image and entrypoint. v0.1 can ignore resources if GPU detection is too complex initially.

### 3. Runner
Responsibilities:
- Resolve paths in config
- Build container run arguments
- Start the container using Docker (Podman later)
- Stream stdout and stderr to the terminal
- Detect run completion and exit code
- Capture timestamps (start, end, duration)

For v0.1, focus on Docker via the CLI (`docker run`) rather than Docker SDK. Keep it simple.

### 4. Storage
Store each run under a root directory, for example:
- `~/.runpilot/runs/<run_id>/`

Contents:
- `config.yaml` (the resolved config)
- `logs.txt`
- `metrics.json` (if any)
- `meta.json` (timestamps, exit code, image, etc)

Additionally, maintain a small SQLite database at:
- `~/.runpilot/runs.db`

Schema (v0.1 simple):
- `runs(id, name, status, started_at, finished_at, exit_code, path)`

### 5. Metrics
v0.1 metrics handling can be very simple:
- Training script writes lines like: \
  `METRIC train_loss=0.123` \
  `METRIC val_accuracy=0.987`

- The runner parses stdout for lines starting with METRIC
- Values are stored in metrics.json as a list of samples

Example metrics.json:
```json
[
  {"step": 1, "train_loss": 0.95},
  {"step": 2, "train_loss": 0.73},
  {"step": 3, "train_loss": 0.51}
]
```
Step can be inferred as a simple counter for v0.1.

### 6. Language and Packaging
- Implemented in Python 3.10+
- Distributed as a Python package with a console script entry point
- Build configuration in pyproject.toml

Example console script entry:
```toml
[project.scripts]
runpilot = "runpilot.cli:main"
```

## Out of scope for v0.1

- Remote execution (SSH, cloud, clusters)
- Kubernetes integration
- Web UI
- Authentication, users and teams
- Rich metrics dashboards
- Framework specific helpers

The goal is a very small but robust core experience: \
`runpilot run config.yaml`

runs a containerised training script, logs everything, and records the run.