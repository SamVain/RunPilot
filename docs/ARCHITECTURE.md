# System Architecture

RunPilot uses a **Distributed, Stateless Architecture**.

It decouples the **Definition** of work (CLI) from the **Coordination** (Cloud) and the **Execution** (Agent).

![RunPilot Diagram](https://via.placeholder.com/800x400?text=RunPilot+Architecture)

## 1. The Client (CLI)
* **Role:** The interface for the Data Scientist.
* **Responsibilities:**
    * Authenticates via JWT.
    * Parses `runpilot.yaml` config.
    * Bundles source code into a `.tar.gz`.
    * Requests a **Presigned S3 Upload URL** from the API.
    * Uploads code directly to AWS S3 (bypassing the API server for speed).

## 2. The Brain (RunPilot Cloud)
* **Stack:** FastAPI + PostgreSQL + Stripe.
* **Hosting:** Render.com.
* **Responsibilities:**
    * **Auth:** Gatekeeper for Pro users (Stripe Integration).
    * **Queue:** Manages job status (`queued`, `running`, `success`, `failed`).
    * **Secrets:** Encrypts and stores environment variables.
    * **Persistence:** Generates secure, time-limited signatures for AWS S3 access.

## 3. The Storage (AWS S3)
* **Role:** The "State" of the system.
* **Location:** `eu-west-2` (London).
* **Data:**
    * **Artifacts:** Source code bundles.
    * **Logs:** Execution logs uploaded by the Agent.
    * **Models:** (Future) Trained model weights.

## 4. The Muscle (Agent)
* **Stack:** Python + Docker + NVIDIA Container Toolkit.
* **Hosting:** Anywhere (Localhost, AWS EC2, On-Prem Cluster).
* **Responsibilities:**
    * Polls the Cloud API for `queued` jobs.
    * Downloads artifacts from S3 using Presigned URLs.
    * **Secrets Injection:** Injects decrypts env vars into the container.
    * **Hardware Access:** Mounts NVIDIA GPUs if `gpu: true` is set.
    * **Isolation:** Runs code inside ephemeral Docker containers.

## The "Golden Loop" Data Flow

1.  **Submit:** User runs `runpilot submit`. Code is zipped and sent to S3. Job is added to Postgres Queue.
2.  **Claim:** Agent polls API, sees job, claims it. Status -> `running`.
3.  **Fetch:** Agent downloads code from S3.
4.  **Execute:** Agent runs Docker. Stream logs to local file.
5.  **Report:** Agent uploads logs to S3 and updates API status -> `success`.