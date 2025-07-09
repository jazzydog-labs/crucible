# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Crucible is a Python CLI tool for AI-assisted ideation and prompt management. It provides a collection of AI prompt templates (blueprints) that can be copied to clipboard and integrates with OpenAI's API.

## Essential Commands

### Running the CLI
```bash
# Interactive blueprint selection
./cru blueprint

# Force selection (ignore memory)
./cru blueprint -s

# Test AI integration
python run_ai.py "Your prompt here"
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_cli.py

# Run with verbose output
python -m pytest -v tests/
```

### Environment Setup
Set OpenAI API key:
- Environment variable: `export OPENAI_API_KEY="your-key"`
- OR create `.OPENAI_API_KEY` file in project root

## Architecture Overview

The project follows a modular monolith design with event-driven architecture:

1. **Entry Points**:
   - `cru` - Main CLI executable
   - `src/cli.py` - CLI command handlers

2. **Core Components**:
   - `src/crucible/ai.py` - OpenAI API integration (currently has hardcoded test values)
   - `src/crucible/event_bus.py` - Simple pub/sub implementation for loose coupling
   - `src/crucible/orchestrator.py` - Event orchestration between components
   - `src/crucible/prompts/generator.py` - Prompt generation logic

3. **Blueprint System**:
   - `blueprints/` - Contains prompt templates as markdown files
   - `blueprints/blueprints.yaml` - Metadata for available blueprints
   - `.crucible.memory` - Stores last selected blueprint

4. **Key Design Decisions**:
   - Event-driven to enable future microservice extraction
   - Uses `pbcopy` for clipboard operations (macOS-specific)
   - Memory persistence for improved UX
   - Structured for future plugin system

## Development Notes

- Python 3.9+ required (uses type annotations and `__future__` imports)
- No package management files exist yet - dependencies are minimal (openai, PyYAML optional)
- AI integration is incomplete - `ai.py` query method needs implementation
- Event bus is implemented but underutilized - ready for future expansion
- **IMPORTANT**: Never truncate or cut off strings in output. Always display full content, especially in demo.py

## Task Management System

This project uses a commit-based task tracking system. Tasks are organized as numbered markdown files in the `commits/` directory:

- `commits/open/` - Contains pending tasks to be implemented
- `commits/closed/` - Contains completed tasks

### Working on Tasks

When implementing a task:
1. Choose a task from `commits/open/` (e.g., `0003_expand_prompt_generation.md`)
2. Read the task description and requirements
3. Implement the changes as specified
4. As part of your commit, move the task file from `open/` to `closed/`:
   ```bash
   git mv commits/open/0003_expand_prompt_generation.md commits/closed/
   git add [your implementation files]
   git commit -m "feat: expand prompt generation logic

   - [implementation details]
   
   Closes: commits/open/0003_expand_prompt_generation.md"
   ```

### Current Open Tasks

Check `commits/open/` for available tasks. Each file contains:
- Detailed requirements
- Proposed implementation approach
- Files that need to be changed
- Architecture considerations

This system helps track granular progress and makes it easy to pick up individual work items.