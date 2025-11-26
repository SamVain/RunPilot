# RunPilot

**The Universal Control Plane for AI/ML Compute.**

RunPilot is an infrastructure-agnostic orchestration tool. It allows you to define a job locally, inject secrets securely, and execute it anywhere—from your laptop to a GPU cluster in the cloud.

### Status
- **Version:** `v0.3.0` (Stable)
- **Platform:** Production (Render + AWS)
- **License:** Apache 2.0

---

## 🚀 Why RunPilot?

Data Scientists shouldn't have to manage Kubernetes manifests, Dockerfiles, or SSH keys just to run a training script.

RunPilot standardizes the workflow:
1.  **Define** your job in a simple YAML.
2.  **Submit** it to the RunPilot Cloud.
3.  **Execute** it on any connected Agent (CPU or GPU).

**Key Features:**
* **Universal Compute:** Works on AWS, GCP, Azure, or your on-prem gaming PC.
* **Secrets Management:** Securely inject `.env` vars into remote containers.
* **Artifact Persistence:** Automatic S3 code bundling and result storage.
* **GPU Native:** Flag-based GPU access (`gpu: true`).

<!-- TODO: Add feature comparison table (CLI vs runpilot-cloud Pro vs Enterprise) -->
<!-- TODO: Add quick demo video/GIF showing submit -> execute flow -->
<!-- TODO: Add badges for PyPI version, downloads, test status -->

---

## 🛠️ Quickstart

### 1. Installation
```bash
pip install git+https://github.com/SamVain/RunPilot.git
```

### 2. Login (Requires Pro Account)
RunPilot Cloud is a paid service for managed orchestration.
```bash
runpilot login
# Follow the prompt to pay and authenticate
```

### 3. Define a Job (`runpilot.yaml`)
```yaml
name: training-run
image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
gpu: true  # <--- Request NVIDIA GPU
entrypoint: python train.py
```

### 4. Submit
```bash
runpilot submit runpilot.yaml --env-file .env
```

See the full [Quickstart Guide](docs/QUICKSTART.md) for details on setting up Agents.

---

## 🏗️ Architecture

RunPilot consists of three components:
1.  **Client (CLI):** Bundles code, encrypts secrets, and talks to the API.
2.  **Cloud (API):** The "Brain". Manages queues, users, and S3 storage links.
3.  **Agent (Worker):** The "Muscle". Polls for jobs and runs them in Docker.

<!-- TODO: Add architecture diagram as an image -->
<!-- TODO: Add link to detailed architecture documentation -->

## Contributing
RunPilot CLI is open source. We welcome PRs!

<!-- TODO: Add CONTRIBUTING.md with guidelines -->
<!-- TODO: Add CODE_OF_CONDUCT.md -->
<!-- TODO: Add issue templates for bugs and feature requests -->
<!-- TODO: Add PR template with checklist -->

## License
Apache 2.0

<!-- TODO: Add section for runpilot-cloud subscription tiers and pricing -->
<!-- TODO: Add FAQ section for common questions -->
<!-- TODO: Add troubleshooting guide -->
<!-- TODO: Add changelog link -->