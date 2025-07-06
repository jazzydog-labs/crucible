# Walking Skeleton

This document describes the initial skeleton for Crucible.

The project starts as a **modular monolith**. Components communicate through a simple in-process event bus so we can later extract them into separate services if needed.

## Components

- **EventBus** – minimal publish/subscribe system used by all modules.
- **Orchestrator** – central coordinator registering handlers and driving the workflow.
- **PromptGenerator** – returns a prompt string; placeholder for future logic.
- **Brainstormer** – accepts a prompt and returns stub ideas.
- **Summarizer** – summarises ideas; currently returns a constant.
- **AI Model Integration** – stub class returning a constant response.

A CLI entry point triggers the orchestrator which then emits events for each step.

## Next Steps

The skeleton will be implemented under `src/crucible`. Each module only prints `"todo: implement this"` and returns stub values. Tests will verify the event bus wiring.
