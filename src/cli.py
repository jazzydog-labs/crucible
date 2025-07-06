"""Project CLI entry point."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Callable, Iterable

from crucible.orchestrator import Orchestrator


BLUEPRINT_DIR = Path(__file__).resolve().parents[1] / "blueprints"
MEMORY_FILE = Path(__file__).resolve().parents[1] / ".crucible.memory"


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


def blueprint_command(
    *,
    memory_file: Path = MEMORY_FILE,
    input_func: Callable[[str], str] = input,
    use_memory: bool = True,
) -> None:
    """Interactive blueprint chooser with *memory-based* default selection.

    1. If a ``.crucible.memory`` file contains the name of an existing
       blueprint, that blueprint is shown *first* in the interactive list.
    2. The prompt defaults to selecting entry *1*; therefore pressing *Enter*
       with no input re-uses the previously chosen blueprint.
    3. The user can still type any number to pick a different blueprint.  The
       new choice is then persisted back to ``.crucible.memory`` for next
       time.

    Passing ``use_memory=False`` skips step 1 entirely (list order is
    untouched, and there is no remembered default).
    """

    # Determine last remembered blueprint (if any).
    last_selection: str | None = None
    if use_memory and memory_file.exists():
        try:
            candidate = memory_file.read_text().strip()
            if candidate and (BLUEPRINT_DIR / candidate).exists():
                last_selection = candidate
        except Exception:  # pragma: no cover – memory errors shouldn't crash.
            pass

    # Build interactive list, moving remembered blueprint to the top.
    blueprints = list_blueprints()
    if last_selection:
        reordered = [bp for bp in blueprints if bp[0] == last_selection]
        reordered.extend(bp for bp in blueprints if bp[0] != last_selection)
        blueprints = reordered

    # Present choices.
    for idx, (name, preview) in enumerate(blueprints, 1):
        print(f"{idx}: {name} - {preview}")

    prompt = "Select blueprint number [1]: "
    raw = input_func(prompt).strip()
    choice = raw or "1"  # Default to first option (remembered or first in list).

    try:
        index = int(choice) - 1
        selected = blueprints[index][0]
    except (ValueError, IndexError):
        print("Invalid selection")
        return

    # Copy to clipboard and persist the choice for next invocation.
    copy_blueprint(selected)
    try:
        memory_file.write_text(selected)
    except Exception:  # pragma: no cover – ignore persistence errors.
        pass

    print(f"Copied {selected} to clipboard")


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Crucible CLI")
    sub = parser.add_subparsers(dest="command")
    bp_parser = sub.add_parser(
        "blueprint", help="Copy a blueprint prompt to clipboard (with memory)"
    )
    bp_parser.add_argument(
        "-s",
        "--select",
        action="store_true",
        help="Force interactive blueprint selection even if a previous choice was remembered.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "blueprint":
        blueprint_command(use_memory=not getattr(args, "select", False))
    else:
        orch = Orchestrator()
        orch.bus.emit("generate_prompt", {"topic": "demo"})


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
