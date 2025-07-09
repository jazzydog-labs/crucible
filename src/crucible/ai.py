"""Simple wrapper around an OpenAI chat model with cost tracking."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Tuple
import openai


class AIModel:
    """Thin wrapper around OpenAI responses with cost tracking.
    """

    GPT_4O_MINI = "gpt-4o-mini"  # Current naming for OpenAI's nano model
    
    # Pricing per 1M tokens (as of 2025)
    PRICING = {
        "gpt-4o-mini": {
            "input": 0.15,   # $0.15 per 1M input tokens
            "output": 0.60   # $0.60 per 1M output tokens
        }
    }

    def __init__(self, api_key: str | None = None, model: str = GPT_4O_MINI) -> None:

        self.model = model
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0

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

    def query(self, prompt: str, max_tokens: int = 200) -> str:
        """Return the assistant's reply for *prompt* using the configured model."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=max_tokens
        )
        
        # Track usage
        if hasattr(response, 'usage'):
            self.total_input_tokens += response.usage.prompt_tokens
            self.total_output_tokens += response.usage.completion_tokens
            self.total_requests += 1
        
        return response.choices[0].message.content.strip()
    
    def get_usage_stats(self) -> Dict[str, any]:
        """Get usage statistics and estimated costs."""
        model_pricing = self.PRICING.get(self.model, self.PRICING[self.GPT_4O_MINI])
        
        # Calculate costs (pricing is per 1M tokens)
        input_cost = (self.total_input_tokens / 1_000_000) * model_pricing["input"]
        output_cost = (self.total_output_tokens / 1_000_000) * model_pricing["output"]
        total_cost = input_cost + output_cost
        
        return {
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "model": self.model
        }
    
    def reset_usage_stats(self) -> None:
        """Reset usage statistics."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0