# Cloud Sync Model

This document outlines how the future RunPilot Cloud service can synchronise runs
from the local CLI. It is intentionally generic so that multiple services or
self-hosted platforms could implement the same API contract.

## Overview

A single training run on the local machine is represented by a directory containing:

* run.json  (metadata)
* metrics.json  (summary metrics)
* logs.txt  (combined stdout and stderr)
* outputs/  (optional artifacts, reports, weights, etc)

RunPilot Cloud aims to be able to:

* list runs by user / project / organisation
* view run metadata, status and metrics
* view or download logs
* store artifacts for long-term access

The sync model relies on:

* a stable run identifier (directory name)
* metadata stored in JSON files
* optional upload of logs and artifacts

## Run Identity

Local run directories use the format:

```
~/.runpilot/runs/<run_id>/
```

Example:

```
20251117T211649Z-hello-run
```

In the cloud, the unique identity becomes:

* tenant_id
* project_id
* run_id

The CLI does not need to understand tenant or project semantics.

## Required and Optional Uploads

Mandatory files per run:

1. run.json
2. metrics.json (if it exists)

Optional but recommended:

* logs.txt
* contents of outputs/

## Local File Schemas

### run.json (example)

```
{
  "id": "20251117T211649Z-hello-run",
  "name": "hello-run",
  "status": "failed",
  "exit_code": 1,
  "created_at": "2025-11-17T21:16:49.832245`00:00",
  "finished_at": "2025-11-17T21:16:49.881217`00:00",
  "image": "python:3.11-slim",
  "entrypoint": "python -c 'print(\"hello from RunPilot stub\")'",
  "run_dir": "/home/user/.runpilot/runs/20251117T211649Z-hello-run",
  "tags": []
}
```

### metrics.json (example)

```
{
  "run_id": "20251117T211649Z-hello-run",
  "summary": {
    "loss": 0.81,
    "accuracy": 0.64,
    "exit_code": 1.0
  },
  "time_series": null,
  "tags": null,
  "recorded_at": "2025-11-17T21:16:49.500000`00:00"
}
```

## Supported Sync Operations

### 1) Register or update run metadata
Input: run.json  
Effect: create or update the run record in the cloud

### 2) Upload metrics
Input: metrics.json  
Effect: store summary metrics and (later) time-series data

### 3) Upload logs
Input: logs.txt file contents  
Effect: store for viewing or download

### 4) Upload artifacts
Input: any file in outputs/  
Effect: associate artifact with run

## Future CLI Integration

A new command will be added:

```
runpilot sync <run-id>
```

Steps performed:

1. Validate run exists locally
2. Upload run.json
3. Upload metrics.json if present
4. Upload logs.txt if present
5. Upload artifacts in outputs/ if present
6. Print cloud link if available

### Cloud Configuration Example

```
# ~/.runpilot/cloud.yaml
api_base_url: "https://api.runpilot.cloud"
token: "rp_XXXXXXXXXXXXXXXX"
default_project: "example-project"
```

Authentication, tenancy and RBAC are enforced server-side only.
The open-source CLI **never handles billing or tenancy logic**.
