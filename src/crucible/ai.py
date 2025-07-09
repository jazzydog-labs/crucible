"""Simple wrapper around an OpenAI chat model."""

from __future__ import annotations

import os
from pathlib import Path
import openai


class AIModel:
    """Thin wrapper around OpenAI responses.
    """

    GPT_4_1_MINI = "gpt-4.1-mini"

    def __init__(self, api_key: str | None = None, model: str = GPT_4_1_MINI) -> None:

        self.model = model

        # ------------------------------------------------------------------
        # API-key discovery – explicit param > env var > dot-file.
        # ------------------------------------------------------------------
        selected_key = api_key or os.getenv("OPENAI_API_KEY")
        if not selected_key:
            key_file = Path.cwd() / ".OPENAI_API_KEY"
            if key_file.exists():
                selected_key = key_file.read_text().strip()


        self.client = openai.OpenAI(api_key=selected_key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def query(self, prompt: str) -> str:
        """Return the assistant's reply for *prompt* using the configured model."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content.strip()