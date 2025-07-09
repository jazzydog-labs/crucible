#!/usr/bin/env python
"""Demo script showing Crucible's AI integration and prompt generation capabilities."""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path
from typing import List, Tuple

# Add src to path for imports
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from crucible.ai import AIModel
from crucible.prompts.generator import PromptGenerator, PromptType
from crucible.ai_observability import demo_ai_budget_info, print_ai_summary


def demo_killer_feature():
    """The ONE thing that makes AI integration amazing."""
    print("=== KILLER FEATURE: AI understands context and generates perfect prompts ===")
    ai = AIModel()
    pg = PromptGenerator(ai_model=ai)
    
    # One line to generate a sophisticated prompt
    prompt = pg.generate({"topic": "startup MVP development"})
    print(f"Generated: {prompt[:100]}...")
    print("\n✨ From topic to tailored prompt in milliseconds - no templates needed!\n")


async def run_demo_async(model: AIModel) -> List[Tuple[str, str, str]]:
    """Run three demo prompts in parallel."""
    
    # Create generators
    pg_ai = PromptGenerator(ai_model=model)
    pg_template = PromptGenerator(ai_model=None)
    
    async def direct_query() -> Tuple[str, str, str]:
        """Direct AI query demo."""
        prompt = "What is domain-driven design in one sentence?"
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, model.query, prompt)
        return ("Direct AI Query", prompt, result)
    
    async def ai_generated() -> Tuple[str, str, str]:
        """AI-powered prompt generation."""
        context = {"topic": "microservices architecture"}
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, pg_ai.generate, context)
        return ("AI Prompt Generation", "microservices architecture", result)
    
    async def template_based() -> Tuple[str, str, str]:
        """Template-based prompt generation (no AI)."""
        context = {
            "prompt_type": PromptType.EVALUATION,
            "topic": "database solutions",
            "options": "PostgreSQL, MongoDB, and DynamoDB",
            "criteria": "performance, scalability, and cost"
        }
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, pg_template.generate, context)
        return ("Template Generation", "database evaluation", result)
    
    # Run all three demos in parallel
    results = await asyncio.gather(
        direct_query(),
        ai_generated(),
        template_based()
    )
    
    return results


def main() -> None:
    """Run streamlined demo."""
    print("\n🚀 Crucible AI Demo")
    print("=" * 50)
    
    # Start with the killer feature
    demo_killer_feature()
    
    # Initialize
    model = AIModel()
    print(f"Model: {model.model}")
    
    # Show AI budget info
    demo_ai_budget_info()
    
    # Time the execution
    start_time = time.time()
    
    print("\n⚡ Running 3 demos in parallel...\n")
    
    # Run async demos
    results = asyncio.run(run_demo_async(model))
    
    # Display results
    for i, (demo_type, input_text, result) in enumerate(results, 1):
        print(f"{i}. {demo_type}")
        print(f"   Input: {input_text}")
        print(f"   Output: {result}")
        print()
    
    # Timing and cost
    elapsed = time.time() - start_time
    stats = model.get_usage_stats()
    
    print(f"⏱️  Time: {elapsed:.2f}s")
    print(f"💰 Cost: ${stats['total_cost']:.4f} ({stats['total_tokens']:,} tokens)")
    
    # Show global AI usage summary
    print_ai_summary()
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()