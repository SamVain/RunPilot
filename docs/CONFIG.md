# Configuration Reference

The `runpilot.yaml` file is the blueprint for your training job.

<!-- TODO: Add JSON schema file for IDE validation/autocomplete -->
<!-- TODO: Add config generator wizard: `runpilot config init` -->

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

<!-- TODO: Add these fields to schema:
| `timeout` | string | Job timeout (e.g., "1h", "30m"). (Default: unlimited) |
| `retries` | integer | Number of retry attempts on failure. (Default: 0) |
| `depends_on` | string[] | List of job IDs this job depends on. |
| `artifacts` | string[] | Output file patterns to upload after completion. |
| `resource_class` | string | Compute tier (e.g., "small", "medium", "gpu-large"). |
| `schedule` | string | Cron expression for scheduled runs. |
-->

## Secrets & Environment Variables

Do **not** commit secrets to `runpilot.yaml`.
Instead, use a local `.env` file and submit it securely:

```bash
runpilot submit runpilot.yaml --env-file .env
```

The agent will inject these variables into the Docker container at runtime.

<!-- TODO: Add support for secrets reference syntax: ${{ secrets.API_KEY }} -->
<!-- TODO: Add secrets management via runpilot-cloud dashboard -->
<!-- TODO: Document secrets encryption and storage -->