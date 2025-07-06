"""Simple wrapper around an OpenAI chat model."""

from __future__ import annotations

import os


class AIModel:
    """Query an OpenAI chat completion model."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-3.5-turbo") -> None:
        try:  # Lazy optional import to keep dependency optional.
            import openai  # type: ignore
        except ModuleNotFoundError as exc:  # pragma: no cover - runtime path
            raise RuntimeError(
                "openai package is required for AIModel but is not installed"
            ) from exc

        self._openai = openai
        self._openai.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._model = model

    def query(self, prompt: str) -> str:
        """Return the assistant message for ``prompt``."""
        response = self._openai.ChatCompletion.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
        )
        return (
            response["choices"][0]["message"]["content"].strip()
            if response.get("choices")
            else ""
        )
