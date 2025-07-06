import sys
import types
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from crucible.ai import AIModel


def test_query_uses_openai():
    # Provide a fake openai module
    dummy_resp = {"choices": [{"message": {"content": "pong"}}]}

    def create(**kwargs):
        return dummy_resp

    dummy = types.SimpleNamespace(
        ChatCompletion=types.SimpleNamespace(create=create)
    )
    sys.modules["openai"] = dummy

    model = AIModel(api_key="test-key", model="test")
    assert model.query("ping") == "pong"

    sys.modules.pop("openai")


def test_missing_openai():
    sys.modules.pop("openai", None)
    try:
        AIModel()
    except RuntimeError as e:
        assert "openai" in str(e)
    else:  # pragma: no cover - should not happen
        assert False
