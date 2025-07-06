"""Project CLI entry point."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Callable, Iterable

from crucible.orchestrator import Orchestrator


BLUEPRINT_DIR = Path(__file__).resolve().parents[1] / "blueprints"


# Optional YAML support. If PyYAML is available, we'll use it to parse blueprint
# metadata that lives alongside the markdown files inside ``blueprints``.  The
# file should be named ``blueprints.yaml`` and contain a simple mapping from the
# markdown filename to a short human-readable summary, e.g.::
#
#     0_domain_expert_persona.md: Domain expert persona and DDD strategist blueprint
#     1_brainstorm_entities.md: Prompts for brainstorming domain model entities
#
# If the YAML file or the ``yaml`` package is not available, the CLI gracefully
# falls back to using the *first* non-blank line of each markdown file as the
# preview (previous behaviour).

# NB: We intentionally make ``yaml`` an *optional* dependency so that the core
# package remains lightweight and unit-tests keep working in minimal
# environments.

try:
    import yaml  # type: ignore

    _HAS_YAML = True
except ModuleNotFoundError:  # pragma: no cover – optional dep.
    yaml = None  # type: ignore
    _HAS_YAML = False


def list_blueprints(directory: Path = BLUEPRINT_DIR) -> list[tuple[str, str]]:
    """Return available blueprints and a short preview/summary.

    The function prefers explicit summaries defined in a companion
    ``blueprints.yaml`` file.  If the YAML metadata file is not present *or*
    cannot be parsed (for example when *PyYAML* is not installed), we fall back
    to extracting the first non-blank line from each markdown file – which
    preserves the original behaviour and keeps legacy tests passing.
    """

    # 1. Attempt to load YAML metadata (optional).
    yaml_path = directory / "blueprints.yaml"
    yaml_mapping: dict[str, str] | None = None

    if yaml_path.exists() and _HAS_YAML:
        try:
            loaded = yaml.safe_load(yaml_path.read_text())  # type: ignore[attr-defined]
            if isinstance(loaded, dict):
                # ensure keys/values are str for our use-case.
                yaml_mapping = {
                    str(k): str(v) for k, v in loaded.items() if isinstance(k, str)
                }
        except Exception:  # pragma: no cover – JSON/YAML errors shouldn't crash.
            yaml_mapping = None

    blueprints: list[tuple[str, str]] = []

    if yaml_mapping:
        # Respect the order as written in the YAML file for nicer UX.
        for name, summary in yaml_mapping.items():
            md_path = directory / name
            if md_path.exists():
                blueprints.append((name, summary))

        # Include any extra markdown files that weren't listed in YAML.
        listed = set(yaml_mapping.keys())
        for path in sorted(directory.glob("*.md")):
            if path.name in listed:
                continue
            first_line = path.read_text().strip().splitlines()[0]
            blueprints.append((path.name, first_line))
    else:
        # Fallback: original implementation – read the first line.
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
