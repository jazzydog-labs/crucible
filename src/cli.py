"""Project CLI entry point."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Callable, Iterable

from crucible.orchestrator import Orchestrator


BLUEPRINT_DIR = Path(__file__).resolve().parents[1] / "blueprints"


def list_blueprints(directory: Path = BLUEPRINT_DIR) -> list[tuple[str, str]]:
    """Return available blueprints and a one line preview."""
    blueprints: list[tuple[str, str]] = []
    for path in sorted(directory.glob("*.md")):
        first_line = path.read_text().strip().splitlines()[0]
        blueprints.append((path.name, first_line))
    return blueprints


def copy_blueprint(
    name: str,
    *,
    directory: Path = BLUEPRINT_DIR,
    run: Callable[..., subprocess.CompletedProcess | None] = subprocess.run,
) -> None:
    """Copy blueprint content to clipboard using pbcopy."""
    path = directory / name
    if not path.exists():
        raise FileNotFoundError(name)
    try:
        run(["pbcopy"], input=path.read_bytes(), check=False)
    except FileNotFoundError:
        print("pbcopy not found; unable to copy to clipboard")


def blueprint_command() -> None:
    """Interactive blueprint chooser."""
    blueprints = list_blueprints()
    for idx, (name, preview) in enumerate(blueprints, 1):
        print(f"{idx}: {name} - {preview}")
    choice = input("Select blueprint number: ")
    try:
        index = int(choice) - 1
        selected = blueprints[index][0]
    except (ValueError, IndexError):
        print("Invalid selection")
        return
    copy_blueprint(selected)
    print(f"Copied {selected} to clipboard")


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Crucible CLI")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("blueprint", help="Copy a blueprint prompt to clipboard")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "blueprint":
        blueprint_command()
    else:
        orch = Orchestrator()
        orch.bus.emit("generate_prompt", {"topic": "demo"})


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
