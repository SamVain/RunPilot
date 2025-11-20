# RunPilot

**The Universal Control Plane for AI/ML Compute.**

RunPilot is an open-core developer tool for defining, running, tracking, and orchestrating computational jobs.

It starts as a local experiment logger on your laptop and scales to become a remote execution engine for your GPU clusters.

### Status
- **CLI**: `v0.2.0` (Stable Beta)
- **Cloud**: `Early Access`

---

## 🚀 Why RunPilot?

Machine Learning infrastructure is a mess of bash scripts, SSH connections, and uncommitted changes.

RunPilot standardizes this:
1.  **Define** your job in a simple YAML.
2.  **Run** it locally for debugging (reproducibility enforced).
3.  **Submit** it to a remote GPU agent with a single command.

We decouple the **definition** of work from the **execution** of work.

## ✨ Features

### 1. Local Reproducibility (Free & Open Source)
Stop asking "which parameters did I use?". RunPilot captures everything automatically.
- **Automatic Tracking:** Captures logs, config, git state, and exit codes.
- **Smart Runner:** Uses Docker if available, gracefully falls back to local processes.
- **Experiment History:** `runpilot list` and `runpilot show` provide a local database of your work.

### 2. Cloud Sync & Collaboration (RunPilot Cloud)
Sync your local runs to the hosted dashboard to share with your team.
- **Central Dashboard:** Visualize metrics and compare runs.
- **Artifact Storage:** Backup code bundles and model weights.
- **Team Visibility:** See what your colleagues are running.

### 3. Remote Orchestration (The Agent)
Turn any machine (AWS instance, on-prem server, gaming PC) into a worker.
- **Bundling:** RunPilot automatically packages your code and requirements.
- **Queueing:** Submit jobs to a centralized queue.
- **Execution:** The RunPilot Agent pulls the job, runs it in a sandbox, and streams logs back to you.

---

## 🛠️ Quickstart

### 1. Installation
```bash
pip install runpilot
```

### 2. Define a job (runpilot.yaml)
```yaml
name: training-run
image: python:3.11-slim
entrypoint: python train.py
params:
  epochs: 10
  lr: 0.001
```

### 3. Run locally
```bash
runpilot run runpilot.yaml
```
Result: Runs on your machine, captures logs to `~/.runpilot/runs/`

### 4. Connect to Cloud (Optional)
```bash
runpilot login
runpilot init  # Select your project
runpilot sync <run_id>
```

### 5. Run Remotely
Start an agent on your GPU server:
```
runpilot agent
```
Submit from your laptop:
```
runpilot submit runpilot.yaml
```
Result: RunPilot bundles your code, uploads it, and the Agent executes it immediately.

---

## 🏗️ Architecture
RunPilot consists of three components:
1. **Client CLI:** Manages local state, bundles artifacts, and communicates with the API.
2. **Cloud (Server):** Stores run history, manages the job queue, and handles artifact storage.
3. **Agent:** Polls the Cloud for `queued` jobs, downloads the code bundle, and executes it in a sandbox.

## Contributing
RunPilot is open source (Apache 2.0). We welcome PRs for the CLI and Local Runner.

## License
RunPilot is licensed under the Apache 2.0 License. See LICENSE for details.