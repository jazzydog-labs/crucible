# Proposed Repository Structure

The project can be organized to reflect domain boundaries and separation of concerns.

```
crucible/
├── README.md
├── blueprints/            # existing brainstorming personas
├── design/                # design documents (this folder)
├── src/
│   ├── crucible/          # main package
│   │   ├── __init__.py
│   │   ├── prompts/
│   │   ├── ideas/
│   │   ├── orchestrator/
│   │   └── plugins/
│   └── cli.py             # command-line entrypoint
├── tests/
└── scripts/
```

- `prompts/` – definitions of prompt templates and meta-prompts.
- `ideas/` – storage and manipulation of idea snippets or brainstorming sessions.
- `orchestrator/` – coordinates plugins, AI agents, and workflows.
- `plugins/` – optional modules loaded at runtime for extra functionality.

This structure keeps the core package in `src/` for isolation while tests and scripts live at the top level.
