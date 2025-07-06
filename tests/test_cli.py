import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from cli import list_blueprints, copy_blueprint, blueprint_command


def test_list_blueprints():
    blueprints = list_blueprints(Path(__file__).resolve().parents[1] / "blueprints")
    names = [bp[0] for bp in blueprints]
    assert "003_codex_expert_implementer.md" in names


def test_copy_blueprint(monkeypatch, tmp_path):
    called = {}

    def fake_run(cmd, *, input, check):
        called["cmd"] = cmd
        called["input"] = input
        called["check"] = check

    blueprint = "001_domain_expert_persona.md"
    copy_blueprint(
        blueprint,
        directory=Path(__file__).resolve().parents[1] / "blueprints",
        run=fake_run,
    )
    assert called["cmd"] == ["pbcopy"]
    assert len(called["input"]) > 0


def test_blueprint_memory_autoselect(monkeypatch, tmp_path):
    """If a memory file exists, blueprint_command should auto-select it."""
    # Arrange: create a temporary memory file pointing to a known blueprint.
    remembered = "001_domain_expert_persona.md"
    mem_path = tmp_path / ".crucible.memory"
    mem_path.write_text(remembered)

    # Patch the module-level MEMORY_FILE so the CLI uses our temp file.
    monkeypatch.setattr("cli.MEMORY_FILE", mem_path, raising=False)

    called = {}

    def fake_copy(name):
        called["name"] = name

    # Monkeypatch copy_blueprint to avoid using pbcopy.
    monkeypatch.setattr("cli.copy_blueprint", lambda name: fake_copy(name))

    # Act – simulate pressing Enter (blank input) so default selects remembered blueprint.
    blueprint_command(memory_file=mem_path, input_func=lambda _: "")

    # Assert
    assert called["name"] == remembered


def test_blueprint_memory_persist(monkeypatch, tmp_path):
    """Interactive choice should be persisted to the memory file."""
    from cli import list_blueprints

    # We will pick the *first* available blueprint.
    first_bp = list_blueprints()[0][0]

    mem_path = tmp_path / ".crucible.memory"

    # Patch MEMORY_FILE and copy_blueprint as above.
    monkeypatch.setattr("cli.MEMORY_FILE", mem_path, raising=False)
    monkeypatch.setattr("cli.copy_blueprint", lambda name: None)

    # Act
    blueprint_command(memory_file=mem_path, input_func=lambda _: "1")

    # Memory file should now contain the selected blueprint.
    assert mem_path.read_text().strip() == first_bp


def test_blueprint_force_select(monkeypatch, tmp_path):
    """use_memory=False should ignore existing memory and use interactive choice."""
    from cli import list_blueprints

    # Existing memory points to a blueprint that is *not* the one we will choose.
    remembered = "001_domain_expert_persona.md"
    mem_path = tmp_path / ".crucible.memory"
    mem_path.write_text(remembered)

    # Patch CLI globals.
    monkeypatch.setattr("cli.MEMORY_FILE", mem_path, raising=False)

    blueprints = list_blueprints()
    second_bp = blueprints[1][0]  # choose 2nd blueprint alphabetically

    chosen = {}
    monkeypatch.setattr("cli.copy_blueprint", lambda name: chosen.setdefault("bp", name))

    # Input "2" to pick second blueprint. use_memory=False.
    blueprint_command(memory_file=mem_path, input_func=lambda _: "2", use_memory=False)

    assert chosen["bp"] == second_bp
    # Memory should update to the new choice.
    assert mem_path.read_text().strip() == second_bp

