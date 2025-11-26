# System Architecture

RunPilot uses a **Distributed, Stateless Architecture**.

It decouples the **Definition** of work (CLI) from the **Coordination** (Cloud) and the **Execution** (Agent).

![RunPilot Diagram](https://via.placeholder.com/800x400?text=RunPilot+Architecture)

<!-- TODO: Replace placeholder with actual architecture diagram -->
<!-- TODO: Add sequence diagrams for key flows (submit, execute, sync) -->

## 1. The Client (CLI)
* **Role:** The interface for the Data Scientist.
* **Responsibilities:**
    * Authenticates via JWT.
    * Parses `runpilot.yaml` config.
    * Bundles source code into a `.tar.gz`.
    * Requests a **Presigned S3 Upload URL** from the API.
    * Uploads code directly to AWS S3 (bypassing the API server for speed).

<!-- TODO: Add support for custom bundling strategies -->
<!-- TODO: Implement client-side validation before submission -->
<!-- TODO: Add progress indicators for long operations -->

## 2. The Brain (RunPilot Cloud)
* **Stack:** FastAPI + PostgreSQL + Stripe.
* **Hosting:** Render.com.
* **Responsibilities:**
    * **Auth:** Gatekeeper for Pro users (Stripe Integration).
    * **Queue:** Manages job status (`queued`, `running`, `success`, `failed`).
    * **Secrets:** Encrypts and stores environment variables.
    * **Persistence:** Generates secure, time-limited signatures for AWS S3 access.

<!-- TODO (runpilot-cloud): Implement subscription tier management -->
<!-- TODO (runpilot-cloud): Add usage billing and quota enforcement -->
<!-- TODO (runpilot-cloud): Implement team/organization management -->
<!-- TODO (runpilot-cloud): Add real-time dashboard with job monitoring -->
<!-- TODO (runpilot-cloud): Implement webhook notifications for job events -->

## 3. The Storage (AWS S3)
* **Role:** The "State" of the system.
* **Location:** `eu-west-2` (London).
* **Data:**
    * **Artifacts:** Source code bundles.
    * **Logs:** Execution logs uploaded by the Agent.
    * **Models:** (Future) Trained model weights.

<!-- TODO: Add multi-region support for lower latency -->
<!-- TODO: Implement automatic cleanup of old artifacts -->
<!-- TODO: Add support for customer-managed S3 buckets (Enterprise) -->

## 4. The Muscle (Agent)
* **Stack:** Python + Docker + NVIDIA Container Toolkit.
* **Hosting:** Anywhere (Localhost, AWS EC2, On-Prem Cluster).
* **Responsibilities:**
    * Polls the Cloud API for `queued` jobs.
    * Downloads artifacts from S3 using Presigned URLs.
    * **Secrets Injection:** Injects decrypts env vars into the container.
    * **Hardware Access:** Mounts NVIDIA GPUs if `gpu: true` is set.
    * **Isolation:** Runs code inside ephemeral Docker containers.

<!-- TODO: Implement agent fleet management dashboard (runpilot-cloud) -->
<!-- TODO: Add support for agent auto-scaling with cloud providers -->
<!-- TODO: Implement agent health monitoring and alerts -->
<!-- TODO: Add support for custom container runtimes (Podman, containerd) -->

<!-- TODO (DAY 2 - runpilot-cloud): Create EC2 Launch Template for auto-provisioning -->
<!-- TODO (DAY 2 - runpilot-cloud): Implement ec2_launcher.py with boto3 -->
<!-- TODO (DAY 2 - runpilot-cloud): Add /v1/runs/{id}/instance/shutdown endpoint -->
<!-- TODO (DAY 2): Add agent --once flag for single-job EC2 execution -->

## The "Golden Loop" Data Flow

1.  **Submit:** User runs `runpilot submit`. Code is zipped and sent to S3. Job is added to Postgres Queue.
2.  **Claim:** Agent polls API, sees job, claims it. Status -> `running`.
3.  **Fetch:** Agent downloads code from S3.
4.  **Execute:** Agent runs Docker. Stream logs to local file.
5.  **Report:** Agent uploads logs to S3 and updates API status -> `success`.

<!-- TODO: Add support for job cancellation at any step -->
<!-- TODO: Implement job retry on transient failures -->
<!-- TODO: Add metrics collection at each step for debugging -->