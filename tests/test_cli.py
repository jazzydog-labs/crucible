import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from cli import list_blueprints, copy_blueprint


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

    blueprint = "0_domain_expert_persona.md"
    copy_blueprint(
        blueprint,
        directory=Path(__file__).resolve().parents[1] / "blueprints",
        run=fake_run,
    )
    assert called["cmd"] == ["pbcopy"]
    assert len(called["input"]) > 0

