# Project Plan

This document outlines a possible path for turning the high level designs into a working prototype.

1. **Decide on Architecture**
   - Start with Option A (Modular Monolith) to keep deployment simple.
   - Keep boundaries clear so pieces can later evolve into services or plugins.

2. **Set Up Repository Skeleton**
   - Create `src/crucible` package with submodules (`prompts`, `ideas`, `orchestrator`, `plugins`).
   - Add basic CLI entry point under `src/cli.py`.
   - Configure testing framework (pytest) and basic CI workflow.

3. **Core Domain Models**
   - Define `Prompt` and `Idea` entities with basic persistence (YAML or JSON files).
   - Implement rendering logic for prompts using context variables.

4. **Orchestrator Prototype**
   - Build a simple orchestrator that loads prompts, expands snippets, and interacts with a dummy AI adapter.
   - Provide hooks for future plugin-based extensions.

5. **Experimentation Loop**
   - Use the orchestrator to run small brainstorming sessions and capture feedback.
   - Document successes and pain points in the `design` directory.

6. **Evaluate Next Steps**
   - After initial experiments, revisit architecture options.
   - Consider breaking out microservices or formalizing the plugin system if necessary.

> **Note**: Many details remain uncertain (data store, type of AI models, etc.). Document decisions as they arise to keep the project grounded.
