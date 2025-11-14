# RunPilot
RunPilot is a lightweight orchestration tool for running reproducible AI training jobs.

You define a training run in a simple YAML config. RunPilot handles the boring parts:
containers, environments, logs, metrics and run history. The goal is to make AI training
feel predictable and repeatable, whether you are on a laptop or a cluster.

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