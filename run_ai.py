#!/usr/bin/env python
"""Quick interactive test for the Crucible ``AIModel`` wrapper.

Usage
-----
python run_ai.py "Prompt text here"

Environment / setup
-------------------
1. Ensure the *openai* package is installed (it is listed in *foundry-bootstrap*).
2. Place your API key in a file named ``.OPENAI_API_KEY`` in the directory
   where you will run this script **or** export ``OPENAI_API_KEY``.

The script adds the local ``src`` directory to *PYTHONPATH* so you can run it
straight from the repository root without installing the package.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make sure local sources are importable when running from repo root.
repo_root = Path(__file__).resolve().parent
sys.path.append(str(repo_root / "src"))

from crucible.ai import AIModel  # noqa: E402  # pylint: disable=wrong-import-position


def main() -> None:
    prompt: str = " ".join(sys.argv[1:]).strip() or "Say hello"

    model = AIModel()
    print(f"Prompt  ➜  {prompt}\n{'-' * 60}")
    try:
        response = model.query(prompt)
        print(response)
    except Exception as exc:  # pragma: no cover – demo script
        print(f"[ERROR] model query failed: {exc}")


if __name__ == "__main__":  # pragma: no cover – manual invocation
    main() 