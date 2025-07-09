#!/usr/bin/env python
"""Demo script showing Crucible's AI integration and prompt generation capabilities."""

from __future__ import annotations

import sys
from pathlib import Path

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


def demo_ai_query(model: AIModel) -> None:
    """Demonstrate direct AI querying."""
    print_section("1. Direct AI Query")
    
    prompt = "What is domain-driven design in one sentence?"
    print(f"Prompt: {prompt}")
    print("-" * 60)
    
    try:
        response = model.query(prompt)
        print(f"Response: {response}")
    except Exception as exc:
        print(f"Error: {exc}")


def demo_basic_prompt_generation(model: AIModel) -> None:
    """Demonstrate basic prompt generation."""
    print_section("2. Basic Prompt Generation")
    
    pg = PromptGenerator(ai_model=model)
    context = {"topic": "microservices architecture"}
    
    print(f"Context: {context}")
    print("-" * 60)
    
    try:
        prompt = pg.generate(context)
        print(f"Generated prompt: {prompt}")
    except Exception as exc:
        print(f"Error: {exc}")


def demo_prompt_types(model: AIModel) -> None:
    """Demonstrate different prompt types."""
    print_section("3. Different Prompt Types")
    
    pg = PromptGenerator(ai_model=model)
    
    # Test different types
    test_cases = [
        (PromptType.ANALYSIS, {"topic": "cloud architecture"}),
        (PromptType.PROBLEM_SOLVING, {"topic": "scalability", "problem": "handling 10x traffic"}),
        (PromptType.SYNTHESIS, {"topic": "AI ethics", "sources": "research papers and industry practices"}),
    ]
    
    for prompt_type, context in test_cases:
        print(f"\n{prompt_type.value.upper()}:")
        context["prompt_type"] = prompt_type
        
        try:
            prompt = pg.generate(context)
            print(f"  {prompt}")
        except Exception as exc:
            print(f"  Error: {exc}")


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


def demo_prompt_chaining(model: AIModel) -> None:
    """Demonstrate prompt chaining for multi-stage workflows."""
    print_section("6. Prompt Chaining")
    
    pg = PromptGenerator(ai_model=model)
    
    # Define a chain of prompts
    chain = [
        {"prompt_type": PromptType.BRAINSTORMING, "topic": "sustainable urban transport"},
        {"prompt_type": PromptType.EVALUATION, "topic": "the generated ideas", "criteria": "feasibility and impact"},
        {"prompt_type": PromptType.REFINEMENT, "topic": "the top ideas", "improvement_areas": "implementation details"}
    ]
    
    print("Prompt chain:")
    for i, p in enumerate(chain, 1):
        print(f"  {i}. {p['prompt_type'].value}: {p['topic']}")
    print("-" * 60)
    
    try:
        results = pg.generate_chain(chain)
        for i, (prompt_def, result) in enumerate(zip(chain, results), 1):
            print(f"\nStep {i} - {prompt_def['prompt_type'].value}:")
            print(f"  {result}")
    except Exception as exc:
        print(f"Error: {exc}")


def main() -> None:
    """Run all demos."""
    print("\n🚀 Crucible AI Integration Demo")
    print("================================")
    
    # Create a shared AI model instance
    model = AIModel()
    print(f"\nUsing model: {model.model}")
    
    # Run each demo
    demo_ai_query(model)
    demo_basic_prompt_generation(model)
    demo_prompt_types(model)
    demo_template_generation()
    demo_custom_template()
    demo_prompt_chaining(model)
    
    # Show cost summary
    print_cost_summary(model)
    
    print("\n\n✅ Demo complete!")
    print("\nNote: Responses are limited to 200 tokens to conserve API usage.")


if __name__ == "__main__":
    main()