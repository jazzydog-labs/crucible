# Blueprint Copy CLI

## Status: CLOSED ✅

## Description
Add a way of copying a prompt from the CLI, by choosing a blueprint, and getting a high level overview of prompts (so we can select which we want, e.g. 003_codex_expert_implementer.md). We can use `pbcopy` (assume we are on mac).

## Implementation Details
- Created blueprint command that lists available prompts
- Added interactive selection mechanism
- Integrated with macOS clipboard using `pbcopy`
- Added memory feature to remember last selection

## Files Changed
- `src/cli.py`
- `blueprints/` directory structure

## Completed
This task was completed in previous commits.