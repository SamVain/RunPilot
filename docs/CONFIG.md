# Configuration format

RunPilot uses YAML configuration files to describe runs.

## Basic schema

Minimal example:

```yaml
name: "mnist-cnn-baseline"
image: "python:3.11-slim"
entrypoint: "python train.py"
params:
  learning_rate: 0.001
  batch_size: 64
  epochs: 10
env:
  PYTHONUNBUFFERED: "1"
tags:
  - "mnist"
  - "cnn"
  - "baseline"
```
Fields:
- `name`: string. Human friendly name for the run.
- `image`: string. Container image to use when Docker is enabled.
- `entrypoint`: string. Command that starts the training job.
- `params`: map of key value pairs. Hyperparameters or configuration keys that should be recorded.
- `env`: map of environment variables to set for the run. Extra environment variables to set for the process.
- `tags`: list of strings. Free form labels for filtering and search later.

## Advanced fields (future)
You may want to support these later:
- `volumes`: list of host to container mounts.
- `resources`: hints such as gpu: 1 or cpu: 4.
- `workdir`: working directory inside the container.

## Project Level Config
In v0.2.x RunPilot should support a project level file such as `runpilot.yaml` in the repository root.
This file can declare named configurations:

```yaml
runs:
  mnist-baseline:
    image: "python:3.11-slim"
    entrypoint: "python train.py"
    params:
      learning_rate: 0.001
      batch_size: 64

  mnist-low-lr:
    extends: mnist-baseline
    params:
      learning_rate: 0.0001

```

Then the CLI could support:
```bash
runpilot run mnist-baseline
```

This is not implemented yet but the schema is chosen to make it easy to add without breaking existing configs.