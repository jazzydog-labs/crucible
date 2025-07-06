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
│   │   ├── event_bus.py
│   │   ├── orchestrator.py
│   │   ├── brainstormer.py
│   │   ├── summarizer.py
│   │   ├── ai.py
│   │   └── plugins/
│   └── cli.py             # command-line entrypoint
├── tests/
└── scripts/
```

- `prompts/` – definitions of prompt templates and meta-prompts.
- `ideas/` – storage and manipulation of idea snippets or brainstorming sessions.
- `event_bus.py` – simple in-process message bus used by modules.
- `orchestrator.py` – coordinates components via the event bus.
- `brainstormer.py` – scaffolding for brainstorming logic.
- `summarizer.py` – collects results and produces summaries.
- `ai.py` – placeholder for AI model integrations.
- `plugins/` – optional modules loaded at runtime for extra functionality.

This structure keeps the core package in `src/` for isolation while tests and scripts live at the top level.
