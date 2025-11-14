# RunPilot Vision

## What is RunPilot

RunPilot is a simple, opinionated orchestration tool for AI training jobs.

It is designed to:

- Make AI training runs reproducible by default
- Reduce the boilerplate around containers, environments and logging
- Provide a clean abstraction that works on a single machine first
- Extend naturally to remote servers and clusters later

The long term goal is for RunPilot to feel like a normal part of the AI workflow, in the same way that Git and Docker feel normal today.

## Problem

Right now AI training often looks like this:

- Ad hoc shell scripts
- Hand written Docker commands
- Environments that drift over time
- Logs saved in random places or not at all
- No easy way to see what was run, with what config and with what result

This causes:

- Wasted GPU time
- Fragile experimentation
- Difficulty reproducing past results
- Pain onboarding new team members
- Poor visibility into how models are actually trained

## RunPilot approach

RunPilot focuses on these principles:

1. **Config first**

   The source of truth for a run is a single config file. You should be able to hand someone a repo and a config file and they can rerun your experiment reliably.

2. **Containers by default**

   Training jobs should run in containers by default. No hidden local dependencies, no mystery environments.

3. **Local first, cluster later**

   v0.1 will only target local execution in containers. Remote and clustered execution are later phases built on the same abstractions.

4. **Structured outputs**

   Logs, metrics and metadata should be stored in a consistent, queryable form so that runs can be compared and audited.

5. **Small surface area**

   The CLI should stay small, predictable and boring. The complexity lives in the implementation, not in the user facing commands.

## Long term direction

Over the next few years RunPilot could grow into:

- A general purpose training orchestration layer for AI teams
- A thin but powerful interface over local machines, remote servers and clusters
- A tool that integrates with cloud providers, GPU vendors and model hosting platforms
- A small ecosystem of plugins for different frameworks and workflows

From a business and strategic point of view, the aim is for RunPilot to become:

- A trusted part of the AI training stack
- A tool that influences how and where compute is consumed
- A piece of infrastructure that is attractive to larger companies in AI, cloud and hardware