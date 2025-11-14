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
