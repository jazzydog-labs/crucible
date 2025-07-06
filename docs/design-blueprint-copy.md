# Blueprint Copy CLI

## Rationale
The first TODO item requests an easy way to copy any of the blueprint prompts from the command line. A lightweight interactive command keeps things simple while avoiding extra dependencies. The command lists available markdown files in `blueprints/`, shows a preview of each, and copies the chosen file to the clipboard via macOS `pbcopy`.

## Approach
- Extend `src/cli.py` with an `argparse` based CLI.
- Add a `blueprint` subcommand that:
  1. Lists blueprint filenames with the first line of text as a preview.
  2. Prompts the user to select one by number.
  3. Pipes the file contents to `pbcopy` using `subprocess.run`.
- The helper functions `list_blueprints()` and `copy_blueprint()` are unit tested directly. `subprocess.run` is mocked so tests remain platform independent.
- A small wrapper script `cru` imports and executes `cli.main()` so the command can be run as `./cru blueprint`.

## Alternatives Considered
- Using a third‑party clipboard library (e.g. `pyperclip`). This was avoided to keep dependencies minimal.
- Implementing a fully interactive TUI. Overkill for the current scope.

## Risks
- `pbcopy` only exists on macOS. The command gracefully fails if it is missing, informing the user.
