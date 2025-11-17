# RunPilot Architecture

This document describes the internal architecture of RunPilot v0.1.x and the direction for v0.2.x and v0.3.x.

The design goal is a simple, reliable core that can support both local only use and a future RunPilot Cloud.

## High level overview

RunPilot has four main concerns:

1. CLI
2. Run management
3. Execution (runners)
4. Storage and metadata

At a high level:

- The CLI parses commands and options.
- The run manager resolves configuration and allocates a run id.
- A runner executes the job (Docker or local process).
- Storage writes `run.json`, `logs.txt` and optional `metrics.json` and artifacts.

## Components

### CLI

Responsibilities:

- Parse subcommands such as `run`, `list`, `show`.
- Load config files.
- Validate user input before execution.
- Call into the run manager.

The CLI should remain thin. Business logic lives in internal modules so that:

- It can be reused by tests.
- Future API or daemon processes can reuse the same logic.

### Run manager

Responsibilities:

- Allocate unique run ids.
- Create the run directory under `~/.runpilot/runs/<run-id>`.
- Persist initial metadata (`run.json` skeleton).
- Select and configure the runner.
- Track status transitions such as `pending`, `running`, `success`, `failed`.

The run manager is the main integration point between CLI, runners and storage.

### Runners

Runners implement a common interface, for example:

- `prepare(run, config)`
- `execute(run, config)`
- `finalise(run, result)`

Current runners:

- Docker runner:
  - Uses a container image.
  - Mounts the run directory if needed.
  - Captures stdout and stderr to `logs.txt`.

- Local runner:
  - Executes a command as a subprocess.
  - Used as a fallback if Docker is not available.

Future runners might include:

- Remote runner for RunPilot Cloud.
- GPU aware runners.
- Queue based runners.

### Storage layout

By default storage is filesystem based:

```text
~/.runpilot/runs/
  <run-id>/
    run.json
    logs.txt
    metrics.json        (optional)
    outputs/            (optional)
      ...
```

The directory name is the primary key for the run.

`run.json` is the canonical metadata record. It is written by the run manager and updated as the run progresses.

In later versions an optional SQLite or remote backend may index runs. The on disk layout is still treated as the source of truth.

## Metrics
Metrics are produced by the training job and written into `metrics.json` inside the run directory.

Design Goals:
- Simple JSON structure.
- Easy to read in CLI or upload to a service.
- Stable across versions.

A proposed schema for v0.2.x is described in `docs/METRICS.md`

## Configuration
For v0.1.x configuration is a YAML file with fields such as:
- `name`
- `image`
- `entrypoint`
- `params`
- `env`
- `tags`

In v0.2.x and later RunPilot will support both:
- Per run configs.
- A project level config file that can define reusable templates.

The config model should be:
- Human writable.
- Stable over time.
- Easy to represent in JSON for a future API.

## Cloud Considerations
The architecture is shaping towards a future where:
- The CLI can sync run metadata with a remote control plane.
- The same run schema is used locally and in the cloud.
- A remote runner can execute jobs while still writing to logical equivalents of run.json, logs.txt and `metrics.json`.

This influences current decisions:
- Use simple, explicit schemas.
- Avoid coupling to a particular database.
- Keep runners behind an interface.