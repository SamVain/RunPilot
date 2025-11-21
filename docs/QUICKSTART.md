# RunPilot Quickstart Guide

This guide takes you from zero to running a remote training job on a GPU worker.

## Prerequisites
* Python 3.10+
* Docker (if running local jobs or hosting an agent)
* A RunPilot Cloud account (Pro)

---

## 1. Setup & Login

Install the CLI:
```bash
pip install git+https://github.com/SamVain/RunPilot.git
```

Login to the Cloud:
```bash
runpilot login
```
*If you don't have an account, the CLI will provide a Stripe Payment Link. Once paid, your account is automatically unlocked via Webhook.*

---

## 2. Create a Project

Link your current folder to a cloud project:
```bash
# Create a new project via API (or ask Admin)
# Then link it:
runpilot init
```

---

## 3. Your First Remote Job

Create a file named `hello_gpu.yaml`:

```yaml
name: hello-gpu
image: ubuntu:22.04
gpu: false # Set to true if you have a GPU worker connected
entrypoint: echo "Hello from the Cloud!"
```

Submit it to the queue:
```bash
runpilot submit hello_gpu.yaml
```

**Success!** Your code is now bundled, uploaded to S3, and waiting in the queue.

---

## 4. Running an Agent (The Worker)

Jobs don't run themselves. You need an **Agent**. You can run this on your laptop, or on a massive AWS EC2 instance.

```bash
runpilot agent
```

The agent will:
1.  Poll the Cloud for your job.
2.  Download your code bundle from S3.
3.  Spin up the Docker container.
4.  Stream logs back to the Cloud Dashboard.

### Running on AWS (Recommended)
To set up a permanent worker on AWS:
1.  Launch a `t2.micro` (CPU) or `g4dn.xlarge` (GPU) instance.
2.  Install Docker and RunPilot.
3.  Run `runpilot login` and `runpilot agent`.