"""Prompt generation logic that utilises the LLM if available."""

from __future__ import annotations

from typing import Any, Mapping, TYPE_CHECKING

# Local import kept inside try-except so the package remains optional for
# environments where ``openai`` is not installed (e.g. CI without network).

if TYPE_CHECKING:  # pragma: no cover
    from ..ai import AIModel

class PromptGenerator:
    """Turn a high-level *context* dict into a concrete brainstorming prompt.

    If the *openai* dependency is available, we delegate to :class:`AIModel` to
    let an LLM craft an expert-level prompt.  Otherwise we fall back to a very
    simple template so the system remains functional (albeit less powerful).
    """

    def __init__(self, ai_model: "AIModel | None" = None):
        # Import lazily to avoid hard dependency on openai for non-AI workflows.
        if ai_model is not None:
            self._ai = ai_model
        else:
            try:
                from ..ai import AIModel  # Local import to sidestep optional dep.

                self._ai = AIModel()
            except Exception:  # pragma: no cover – missing dependency etc.
                # We store *None* so generate() can detect unavailable AI.
                self._ai = None

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------

    def generate(self, context: Mapping[str, Any] | None = None) -> str:
        """Return a prompt string derived from *context*.

        Expected keys in *context*:
        - ``topic``: short description of what we are brainstorming about.
        """

        context = context or {}
        topic = context.get("topic", "an unspecified topic")

        # If we have an AI model available, delegate prompt wording to it.
        if self._ai is not None:
            system_instruction = (
                "You are an expert brainstorming facilitator. "
                "Craft a concise prompt that will encourage creative, high-level "
                "thinking about the given topic. Return *only* the prompt text."
            )
            full_prompt = f"{system_instruction}\n\nTopic: {topic}"

            try:
                return self._ai.query(full_prompt)
            except Exception as exc:  # pragma: no cover – network/API issues.
                # Fall through to the basic template below.
                print(f"AIModel error – using fallback prompt. Detail: {exc}")

        # Fallback – keep the system usable without external dependencies.
        return f"Brainstorm innovative ideas related to '{topic}'."
