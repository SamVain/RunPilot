# RunPilot Development Roadmap

This document outlines the development tasks for RunPilot (open-source CLI) and its integration with runpilot-cloud (paid compute-UI platform).

---

## 🔥 Immediate Tasks (Day 2) - EC2 Auto-Run Infrastructure

### AWS IAM Setup (runpilot-cloud)
- [ ] Create IAM role for EC2 instances
  - Trusted entity: EC2
  - Attach AmazonEC2FullAccess policy
  - Attach AmazonS3FullAccess policy
- [ ] Create more restrictive IAM policies for production

### EC2 Launch Template (runpilot-cloud)
- [ ] Create EC2 Launch Template: `runpilot-cpu-template`
  - Instance type: t3.small
  - AMI: Ubuntu 22.04
  - User-data script to:
    - Install Docker
    - Install Python
    - pip install runpilot-agent
    - Run `runpilot agent --once`

### EC2 Launcher Service (runpilot-cloud)
- [ ] Create `cloud/services/ec2_launcher.py`
  - boto3 code to launch instances from template
  - Wait for instance to enter "running" state
  - Return instance ID
  - Handle launch failures gracefully

### EC2 Shutdown Endpoint (runpilot-cloud)
- [ ] Add API endpoint: `POST /v1/runs/{id}/instance/shutdown`
- [ ] Implement boto3.terminate_instances call
- [ ] Agent calls this endpoint after job completion
- [ ] Add instance cleanup for orphaned/stale instances

### Agent Enhancements (RunPilot CLI)
- [ ] Add `runpilot agent --once` flag for single-job execution
- [ ] Implement auto-shutdown after job completion
- [ ] Add instance metadata reporting to cloud

### End-to-End Validation
- [ ] Test complete flow: submit → EC2 launch → agent run → shutdown
- [ ] Verify logs are uploaded before instance termination
- [ ] Test failure scenarios (job fails, instance dies, etc.)

---

## 🎯 High Priority

### CLI Enhancements
- [ ] Add `runpilot logs <run_id>` command to stream/view logs
- [ ] Add `runpilot cancel <run_id>` command to cancel queued/running jobs
- [ ] Add `runpilot status` command for quick status overview
- [ ] Implement `runpilot watch <run_id>` for real-time job monitoring
- [ ] Migrate from argparse to Click for better UX

### Agent Improvements
- [ ] Implement agent registration with unique agent_id
- [ ] Add agent heartbeat mechanism for status tracking
- [ ] Support agent labels/tags for job routing (e.g., gpu:a100, region:eu)
- [ ] Implement graceful shutdown with job completion

### Core Features
- [ ] Add job cancellation support at any stage
- [ ] Implement job retry on transient failures
- [ ] Add container health checks during execution

---

## 🔐 Authentication & Security

### Authentication
- [ ] Add OAuth2 login flow with browser-based authentication
- [ ] Support SSO/SAML for enterprise customers
- [ ] Add MFA/2FA support
- [ ] Implement token refresh mechanism
- [ ] Add `runpilot logout` command
- [ ] Support multiple profiles with --profile flag

### Security
- [ ] Implement client-side encryption for sensitive code
- [ ] Add config file permissions checking
- [ ] Implement run encryption at rest
- [ ] Add archive signing for integrity verification

---

## 📦 Configuration & Projects

### Config System
- [ ] Add schema validation with detailed error messages (pydantic)
- [ ] Support environment variable interpolation (${VAR_NAME})
- [ ] Support config inheritance (base + overrides)
- [ ] Add timeout field for job execution limits
- [ ] Add retry_count field for automatic retries
- [ ] Add depends_on field for job dependencies
- [ ] Add resource_class field for tier-based compute

### Project Management
- [ ] Add `runpilot project create <name>` command
- [ ] Implement project-level default configurations
- [ ] Add project templates with pre-configured settings
- [ ] Support project environments (dev, staging, prod)

---

## 🐳 Container & Execution

### Docker Improvements
- [ ] Implement container image caching
- [ ] Add support for private Docker registries
- [ ] Implement container memory/CPU profiling
- [ ] Add support for Docker Compose multi-container jobs
- [ ] Support additional volumes via config
- [ ] Implement log rotation for long-running jobs

### Alternative Runtimes
- [ ] Add support for Podman
- [ ] Add support for Singularity (HPC environments)
- [ ] Add support for containerd

---

## 📊 Metrics & Monitoring

### Metrics System
- [ ] Add support for custom metric types (gauge, counter, histogram)
- [ ] Implement metric aggregation across distributed jobs
- [ ] Add support for TensorBoard log parsing
- [ ] Implement W&B (Weights & Biases) integration
- [ ] Add support for MLflow metrics format
- [ ] Implement real-time metric streaming to dashboard

### Monitoring
- [ ] Implement agent resource reporting (CPU, memory, GPU)
- [ ] Add job duration tracking
- [ ] Implement container memory/CPU profiling
- [ ] Add agent health monitoring and alerts

---

## ☁️ Cloud Integration (runpilot-cloud)

### Subscription Tiers
- [ ] Implement subscription tier management
- [ ] Add usage billing and quota enforcement
- [ ] Add cost estimation before job submission
- [ ] Implement bundle size limits per tier
- [ ] Gate features by subscription level

### Dashboard Features
- [ ] Add real-time job monitoring dashboard
- [ ] Implement agent fleet management view
- [ ] Add run comparison (side-by-side diffs)
- [ ] Implement project activity feed and audit log

### Team Features
- [ ] Implement team/organization management
- [ ] Add project team members and permissions
- [ ] Support organization-level config sharing
- [ ] Add project-level secrets management

### Notifications
- [ ] Implement webhook notifications for job events
- [ ] Add email/Slack notifications on completion
- [ ] Add configurable alerting thresholds

---

## 🔧 Infrastructure & Deployment

### Agent Deployment
- [ ] Add CloudFormation templates for AWS deployment
- [ ] Add Terraform templates for multi-cloud
- [ ] Add Kubernetes deployment manifests
- [ ] Implement agent auto-scaling integration

### Storage
- [ ] Add multi-region S3 support
- [ ] Implement automatic artifact cleanup
- [ ] Add support for customer-managed S3 buckets (Enterprise)
- [ ] Support remote storage backends (S3, GCS, Azure Blob)

---

## 📖 Documentation & Developer Experience

### Documentation
- [ ] Replace architecture diagram placeholder with actual diagram
- [ ] Add video walkthrough of quickstart
- [ ] Add CONTRIBUTING.md guidelines
- [ ] Add CODE_OF_CONDUCT.md
- [ ] Create issue and PR templates
- [ ] Add troubleshooting guide
- [ ] Add FAQ section

### CLI Experience
- [ ] Add shell completion (bash, zsh, fish)
- [ ] Add --verbose/-v flag for debug output
- [ ] Add --quiet/-q flag for CI/CD
- [ ] Add --output-format flag (json, yaml, table)
- [ ] Add progress bars for uploads
- [ ] Implement `runpilot doctor` command for prerequisites check

### Distribution
- [ ] Publish to PyPI
- [ ] Add Homebrew formula for macOS
- [ ] Create Docker image for CLI
- [ ] Implement `runpilot upgrade` self-update command

---

## 🔮 Future Features

### Advanced Job Features
- [ ] Support multi-step pipelines
- [ ] Implement job scheduling (cron syntax)
- [ ] Add job dependencies (--depends-on)
- [ ] Implement job checkpointing for long tasks
- [ ] Support Git-based code fetching

### Enterprise Features
- [ ] Add `runpilot ssh <agent_id>` for debugging
- [ ] Implement run sharing via public links
- [ ] Add project cloning/forking
- [ ] Support customer-managed infrastructure

### Integrations
- [ ] GitHub Actions integration
- [ ] GitLab CI integration
- [ ] VS Code extension
- [ ] JupyterHub plugin

---

## 🏷️ Legend

- **RunPilot CLI**: Open-source command-line tool
- **runpilot-cloud**: Paid SaaS platform with dashboard, billing, and team features
- **Pro Feature**: Available in paid tiers
- **Enterprise Feature**: Available in enterprise tier only

---

*Last updated: 2024*
