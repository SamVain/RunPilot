# Configuration Reference

The `runpilot.yaml` file is the blueprint for your training job.

## Minimal Example
```yaml
name: my-experiment
image: python:3.11-slim
entrypoint: python train.py
```

## GPU Example
```yaml
name: deep-learning-job
image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
gpu: true
entrypoint: python train.py --epochs 100
```

## Schema

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | string | **Required.** Unique name for the run directory. |
| `image` | string | **Required.** Docker image to use (e.g., `ubuntu:22.04`). |
| `entrypoint` | string | **Required.** The command to run inside the container. |
| `gpu` | boolean | If `true`, requests NVIDIA GPU access. (Default: `false`) |

## Secrets & Environment Variables

Do **not** commit secrets to `runpilot.yaml`.
Instead, use a local `.env` file and submit it securely:

```bash
runpilot submit runpilot.yaml --env-file .env
```

The agent will inject these variables into the Docker container at runtime.