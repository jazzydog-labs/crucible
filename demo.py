#!/usr/bin/env python
"""Demo script showing Crucible's AI integration and prompt generation capabilities."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from crucible.ai import AIModel
from crucible.prompts.generator import PromptGenerator, PromptType, PromptTemplate


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print('=' * 60)


def print_cost_summary(model: AIModel) -> None:
    """Print cost summary for API usage."""
    stats = model.get_usage_stats()
    print(f"\n💰 API Usage Summary:")
    print(f"  Model: {stats['model']}")
    print(f"  Requests: {stats['total_requests']}")
    print(f"  Input tokens: {stats['total_input_tokens']:,}")
    print(f"  Output tokens: {stats['total_output_tokens']:,}")
    print(f"  Total tokens: {stats['total_tokens']:,}")
    print(f"  Estimated cost: ${stats['total_cost']:.4f}")


async def async_generate_prompt(pg: PromptGenerator, context: Dict[str, Any]) -> str:
    """Generate a prompt asynchronously."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, pg.generate, context)


async def async_query(model: AIModel, prompt: str) -> str:
    """Query the AI model asynchronously."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, model.query, prompt)


async def demo_all_prompts(model: AIModel) -> Dict[str, List[Tuple[str, str]]]:
    """Generate all demo prompts in parallel and return results."""
    results = {}
    
    # Direct AI Query
    query_task = async_query(model, "What is domain-driven design in one sentence?")
    
    # Basic Prompt Generation
    pg = PromptGenerator(ai_model=model)
    basic_context = {"topic": "microservices architecture"}
    basic_task = async_generate_prompt(pg, basic_context)
    
    # Different Prompt Types
    prompt_type_contexts = [
        (PromptType.ANALYSIS, {"topic": "cloud architecture"}),
        (PromptType.PROBLEM_SOLVING, {"topic": "scalability", "problem": "handling 10x traffic"}),
        (PromptType.SYNTHESIS, {"topic": "AI ethics", "sources": "research papers and industry practices"}),
    ]
    
    prompt_type_tasks = []
    for prompt_type, context in prompt_type_contexts:
        context["prompt_type"] = prompt_type
        task = async_generate_prompt(pg, context)
        prompt_type_tasks.append((prompt_type, task))
    
    # Prompt Chaining
    chain = [
        {"prompt_type": PromptType.BRAINSTORMING, "topic": "sustainable urban transport"},
        {"prompt_type": PromptType.EVALUATION, "topic": "the generated ideas", "criteria": "feasibility and impact"},
        {"prompt_type": PromptType.REFINEMENT, "topic": "the top ideas", "improvement_areas": "implementation details"}
    ]
    
    chain_tasks = []
    for prompt_def in chain:
        task = async_generate_prompt(pg, prompt_def)
        chain_tasks.append((prompt_def, task))
    
    # Wait for all tasks to complete
    print("\n⏳ Generating all prompts in parallel...")
    
    # Collect Direct AI Query result
    query_result = await query_task
    results["direct_query"] = [("What is domain-driven design in one sentence?", query_result)]
    
    # Collect Basic Prompt result
    basic_result = await basic_task
    results["basic"] = [(str(basic_context), basic_result)]
    
    # Collect Prompt Type results
    prompt_type_results = []
    for prompt_type, task in prompt_type_tasks:
        result = await task
        prompt_type_results.append((prompt_type.value.upper(), result))
    results["prompt_types"] = prompt_type_results
    
    # Collect Chain results
    chain_results = []
    for prompt_def, task in chain_tasks:
        result = await task
        chain_results.append((f"{prompt_def['prompt_type'].value}: {prompt_def['topic']}", result))
    results["chain"] = chain_results
    
    print("✅ All prompts generated successfully!\n")
    
    return results


def display_results(results: Dict[str, List[Tuple[str, str]]]) -> None:
    """Display all collected results."""
    
    # Direct AI Query
    print_section("1. Direct AI Query")
    prompt, response = results["direct_query"][0]
    print(f"Prompt: {prompt}")
    print("-" * 60)
    print(f"Response: {response}")
    
    # Basic Prompt Generation
    print_section("2. Basic Prompt Generation")
    context, prompt = results["basic"][0]
    print(f"Context: {context}")
    print("-" * 60)
    print(f"Generated prompt: {prompt}")
    
    # Different Prompt Types
    print_section("3. Different Prompt Types")
    for prompt_type, result in results["prompt_types"]:
        print(f"\n{prompt_type}:")
        print(f"  {result}")
    
    # Template-Based Generation (No AI) - This runs synchronously
    demo_template_generation()
    
    # Custom Template - This runs synchronously
    demo_custom_template()
    
    # Prompt Chaining
    print_section("6. Prompt Chaining")
    print("Prompt chain:")
    for i, (desc, _) in enumerate(results["chain"], 1):
        print(f"  {i}. {desc}")
    print("-" * 60)
    
    for i, (desc, result) in enumerate(results["chain"], 1):
        print(f"\nStep {i} - {desc.split(':')[0]}:")
        print(f"  {result}")


def demo_template_generation() -> None:
    """Demonstrate template-based generation without AI."""
    print_section("4. Template-Based Generation (No AI)")
    
    # Create generator without AI
    pg = PromptGenerator(ai_model=None)
    
    context = {
        "prompt_type": PromptType.EVALUATION,
        "topic": "database solutions",
        "options": "PostgreSQL, MongoDB, and DynamoDB",
        "criteria": "performance, scalability, and cost"
    }
    
    print(f"Context: {context}")
    print("-" * 60)
    
    try:
        prompt = pg.generate(context)
        print(f"Template prompt: {prompt}")
    except Exception as exc:
        print(f"Error: {exc}")


def demo_custom_template() -> None:
    """Demonstrate custom template creation."""
    print_section("5. Custom Template")
    
    pg = PromptGenerator()
    
    # Add a custom template
    custom_template = PromptTemplate(
        "As a {role}, analyze {topic} and provide {num_recommendations} recommendations "
        "focusing on {focus_area}. Consider {constraints} in your analysis."
    )
    
    pg.add_template("custom_analysis", custom_template)
    
    # Use the custom template by rendering it directly
    context = {
        "role": "security expert",
        "topic": "API authentication methods",
        "num_recommendations": "5",
        "focus_area": "zero-trust architecture",
        "constraints": "backwards compatibility"
    }
    
    print("Custom template added: 'custom_analysis'")
    print(f"Context: {context}")
    print("-" * 60)
    
    try:
        prompt = custom_template.render(context)
        print(f"Custom prompt: {prompt}")
    except Exception as exc:
        print(f"Error: {exc}")


async def main() -> None:
    """Run all demos."""
    print("\n🚀 Crucible AI Integration Demo")
    print("================================")
    
    # Create a shared AI model instance
    model = AIModel()
    print(f"\nUsing model: {model.model}")
    
    # Run all async demos in parallel
    results = await demo_all_prompts(model)
    
    # Display all results
    display_results(results)
    
    # Show cost summary
    print_cost_summary(model)
    
    print("\n\n✅ Demo complete!")
    print("\nNote: Responses are limited to 200 tokens to conserve API usage.")


if __name__ == "__main__":
    asyncio.run(main())