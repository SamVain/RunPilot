# RunPilot

RunPilot is a lightweight orchestration tool for running reproducible AI training jobs.

You define a training run in a simple YAML config. RunPilot handles the boring parts:
containers, environments, logs, metrics and run history. The long-term goal is to make AI
training feel predictable and repeatable, whether you are on a laptop or a cluster.

> Status: Very early. v0.1 is under active development.

---

## Vision
RunPilot should become the easiest way to:

- Define a training run in a single config file
- Run that training job locally in a container
- Capture logs and metrics in a structured way
- Keep a history of runs for comparison and reproducibility
- Later: extend the same flow to remote servers and clusters

Think of it as Docker Compose for AI training jobs.

## v0.1 MVP

The first version of RunPilot focuses on a very small but solid feature set:

- A `runpilot` CLI
- A YAML based run configuration format
- Local Docker or Podman based execution of training jobs
- Streaming logs to the console and saving them per run
- Simple metrics extraction from stdout and saving to a file
- A lightweight run history stored in SQLite

Details are in [`docs/mvp-v0.1.md`](docs/mvp-v0.1.md).

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
entrypoint: "python -c 'print(\"hello from RunPilot stub\")'"
```

### 5. Run it!
```bash
runpilot run example.yaml
```

Right now, this will just print what it would do. Future versions will actually run
containers, capture logs, metrics and store run history.

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
RunPilot is currently in the design and prototyping phase.
Our current goals are to:
- Define a vision and scope
- lock in the v0.1 MVP
- Set up a basic project structure and tooling

If you find this repo and it looks empty, it just means the work is still in the very early stages.

---

## License
Planned: MIT or Apache 2.0 (to be finalised).